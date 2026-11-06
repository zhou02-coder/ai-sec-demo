import asyncio
import hmac
import hashlib
import time
import uuid
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field

# 1. 日志与追踪系统配置（标准工业级格式：时间 + 线程/协程追踪 ID + 级别 + 消息）
logging.basicConfig(level=logging.INFO, 
                    format="[%(asctime)s.%(msecs)03d] [%(levelname)s] [ReqID: %(trace_id)s] %(message)s",datefmt="%H:%M:%S")

# 自定义 Extra 兼容适配器，保证日志必定带有 trace_id（追踪ID）
class TraceLogger(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs.setdefault("extra", {})
        kwargs["extra"].setdefault("trace_id", self.extra.get("trace_id", "SYSTEM"))
        return msg, kwargs

logger = TraceLogger(logging.getLogger("AsyncGateway"), {"trace_id": "INIT"})

# ==============================================================================
# 数据模型与异常体系（域驱动设计 DDD 与多阶异常分类）
# ==============================================================================

class GatewayEXception(Exception):
    """网关基础异常"""
    pass

class AuthenticationError(GatewayEXception):
    """身份鉴权失败 (签名非法/重放攻击)"""
    pass

class RateLimitExceedeError(GatewayEXception):
    """超出速率限制 (触发 Dos/CC 防护)"""
    pass

class TaskTimeoutException(GatewayEXception):
    """下游超时熔断"""
    pass

@dataclass
class EncryptedRequestPayload:
    """网关标准请求载荷 (模拟 HTTP/2 异步数据流) """
    request_id: str
    client_ip: str
    timestamp: float  # 浮点数，带有小数点的数字
    data: str
    signature: str    # HMAC-SHA256 签名，防篡改

@dataclass
class ProcessingResult:
    """网关处理结果打包"""
    request_id: str
    status_code: int
    payload_response: Optional[str]
    error_message: Optional[str]
    execution_time_ms: float

# ==============================================================================
# 安全防御核心组件 1：分布式 Token 桶异步限流器（防 CC 攻击与高并发冲垮）
# ==============================================================================

class AsyncTokenBucketRateLimiter:
    """
    【防御机制: 异步平滑 Token 桶限流器】
    设计意图: 防止恶意客户端短时间内发起倾泻式请求 (Burst Attack)。
    知识点: 利用 asyncio.Lock 保证令牌补充与消耗的原子性, 支持平滑漏桶/令牌桶算法。
    """
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity      # 桶容量（最大突发并发数）
        self.refill_rate = refill_rate    # 令牌填充速率（个/秒）
        self.tokens = float(capacity)
        self.last_refill_timestamp = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self, client_ip: str) -> bool:
        """尝试获取 1 个令牌, 获取失败立即拦截, 防止协程卡死"""
        async with self._lock:
            now = time.time()
            # 动态计算从上次到现在需要补充的令牌数
            elapsed = now - self.last_refill_timestamp
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill_timestamp = now

            if self.tokens >= 1.0:
                self.tokens -= 1.0   # 如果硬币足够，便扣除一个，让其通过进来
                return True
            else:
                # 令牌不足，拦截流量
                return False
            
# ==============================================================================
# 安全防御核心组件 2：防重放攻击与 HMAC 签名校验器（API 数据完整性）
# ==============================================================================

class SecurityAuthenticator:
    """
    【防御机制: API 数据完整性与防重放攻击 (Anti-Replay Attack)】
    设计意图: 
        1. 校验请求时间戳是否超出安全窗口 (例如5秒), 防止攻击者抓包后重放。
        2. 校验 HMAC-SHA256 签名, 防中间人篡改 (MITM)。
        """
    def __init__(self, secret_key: str, max_clock_skew: float = 5.0):
        self.secret_key =secret_key.encode('utf-8')
        self.max_clock_skew = max_clock_skew
        # 用于记录已处理过的 request_id，防止在安全时间窗口内的重复提交（简易 BloomFilter 替代方案）
        self._seen_request_ids: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def verify_request(self, payload: EncryptedRequestPayload) -> None:
        now = time.time()

        # 1. 时间戳漂移检测（防重放）
        if abs(now - payload.timestamp) > self.max_clock_skew:
            raise AuthenticationError(f"请求超时或者存在时间戳重放风险, 当前偏离: {abs(now - payload.timestamp):.2f}s")

        # 2. 检查 request_id 是否被复用
        async with self._lock:
            if payload.request_id in self._seen_request_ids:
                raise AuthenticationError(f"检测到重复的 request_id: {payload.request_id}, 疑似重放攻击! ")
            self._seen_request_ids[payload.request_id] = now

            # 定期清理过期的 ID 缓存，防止内存泄漏（Memory Leak 防御）
            if len(self._seen_request_ids) > 1000:
                self._seen_request_ids = {k: v for k, v in self._seen_request_ids.items()
                                          if now - v <= self.max_clock_skew}

        # 3. HMAC-SHA256 签名验证（防篡改）
        raw_content = f"{payload.request_id}:{payload.timestamp}:{payload.data}".encode('utf-8')
        expected_sig = hmac.new(self.secret_key, raw_content, hashlib.sha256).hexdigest()

        # s使用 hmac.compare_digest 防止时序攻击（Timing Attack）
        if not hmac.compare_digest(expected_sig, payload.signature):
            raise AuthenticationError("签名校验失败! 数据在传输过程中可能遭到中间人篡改。")

# ==============================================================================
# 工业级高并发异步处理引擎（含生产者-消费者模型、死信队列、优雅停机）
# ==============================================================================

class SafeAsyncGatewayEngine:
    """
    【高并发全特性异步微服务网关引擎】
    包含特性: 
        - 异步队列解耦 (Async Queue)
        - 线程安全信号量背压控制 (Semaphore)
        - 死信队列 (Dead Letter Queue, DLQ) 用于保存彻底失败的异常任务
        - 优雅停机 (Graceful Shutdown): 处理完队列存量任务后再安全退出
    """
    def __init__(self, worker_concurrency: int = 4, queue_max_size: int = 100,
                 request_timeout: float = 1.2, secret_key: str = "Hardened_Architect_Secret_2026"):
        self.worker_concurrency = worker_concurrency
        self.request_timeout = request_timeout

        # 异步主任务队列（有界队列，超出引发背压）
        self.task_queue: asyncio.Queue[EncryptedRequestPayload] = asyncio.Queue(maxsize=queue_max_size)

        # 异常死信队列（DLQ）
        self.dead_letter_queue: asyncio.Queue[ProcessingResult] = asyncio.Queue()

        # 依赖组件
        self.rate_limiter = AsyncTokenBucketRateLimiter(capacity=5, refill_rate=2.0)
        self.authenticator =SecurityAuthenticator(secret_key=secret_key)
        self.semaphore = asyncio.Semaphore(worker_concurrency)

        # 引擎状态标记
        self.is_running = False
        self.workers: list[asyncio.Task] = []
        self._processed_count = 0
        self._count_lock = asyncio.Lock()

    async def generate_signature(self, request_id: str, timestamp: float, data: str):
        """辅助方法: 客户端生成 HMAC 签名的函数"""
        raw_content = f"{request_id}:{timestamp}:{data}".encode('utf-8')
        return hmac.new(self.authenticator.secret_key, raw_content, hashlib.sha256).hexdigest()

    async def submit_request(self, payload: EncryptedRequestPayload) -> bool:
        """
        【入口流量控制】
        向网关队列提交任务。若队列满, 阻止无限灌入, 实现背压机制
        """
        if not self.is_running:
            raise RuntimeError("网关未启动, 拒绝接受新流量! ")

        try:
            # wait_for 设定队列写入超时，防止客户端无休止挂起
            await asyncio.wait_for(self.task_queue.put(payload), timeout=0.5)
            logger.info(f" 请求已进入网关队列 [队列深度: {self.task_queue.qsize()}]", extra={"trace_id": payload.request_id})
            return True
        except asyncio.TimeoutError:
            logger.warning(f" 网关队列已爆满, 触发流量拒绝 (Backpressure Limit)", extra={"trace_id": payload.request_id})
            return False
        
    async def _process_single_payload(self, payload: EncryptedRequestPayload) -> ProcessingResult:
        """
        【全链路异步管线核心】: 限流校验 -> 安全鉴权 -> 业务处理 -> 异常处理
        """
        start_time = time.time()
        log = TraceLogger(logging.getLogger("Worker"), {"trace_id": payload.request_id})

        async with self.semaphore:
            try:
                # Step 1：异步速率限制防护
                if not await self.rate_limiter.acquire(payload.client_ip):
                    raise RateLimitExceedeError(f"客户端 IP [{payload.client_ip}] 触发速率限制")

                # Step 2：签名与重放安全防护
                await self.authenticator.verify_request(payload)

                # Step 3：执行实际下游业务逻辑（包裹在超时熔断机制中）
                # 使用 wait_for 防止下游业务（数据库/第三方远程 RPC）卡死
                response_data = await asyncio.wait_for(self._mock_downstream_microservice(payload.data),
                                                       timeout=self.request_timeout)

                elapsed = (time.time() - start_time) * 1000
                log.info(f" 流量处理成功! 响应耗时: {elapsed:.2f}ms")

                async with self._count_lock:
                    self._processed_count += 1

                return ProcessingResult(request_id=payload.request_id,
                                        status_code=200,
                                        payload_response=response_data,
                                        error_message=None,
                                        execution_time_ms=elapsed)
            except RateLimitExceedeError as e:
                log.warning(f" [防御拦截-429 Too Many Requests]: {str(e)}")
                return ProcessingResult(payload.request_id, 429, None, str(e), (time.time() - start_time) * 1000)

            except AuthenticationError as e:
                log.error(f"🔒 [防御拦截-401 Unauthorized]: {str(e)}")
                return ProcessingResult(payload.request_id, 401, None, str(e), (time.time() - start_time) * 1000)

            except asyncio.TimeoutError:
                log.error(f"💣 [熔断拦截-504 Gateway Timeout]: 下游微服务响应超时（超过 {self.request_timeout}s)")
                return ProcessingResult(payload.request_id, 504, None, "Downstream Service Timeout", (time.time() - start_time) * 1000)

            except Exception as e:
                # 兜底捕获未预期的运行时崩溃（例如语法错误、内存溢出）
                log.critical(f"🔥 [系统崩溃-500 Internal Error]: 捕获未处理异常: {type(e).__name__} - {str(e)}")
                return ProcessingResult(payload.request_id, 500, None, f"Fatal: {str(e)}", (time.time() - start_time) * 1000)
    
    async def _mock_downstream_microservice(self, data: str) -> str:
        """模拟复杂的异步下游微服务 (数据库读写、加密运算等)"""
        # 制造模拟故障逻辑
        if "malicious_sql" in data:
            raise ValueError("SQL注入特征码检测触发! 阻止执行。")
        elif "slow_payload" in data:
            await asyncio.sleep(2.5)  # 故意休眠超过 1.2s，诱发 504 超时熔断
        else:
            await asyncio.sleep(0.2)  # 正常业务处理耗时

        return f"PROCESSED_SUCCESSFULLY: [{data.upper()}]"
    
    async def _worker_loop(self, worker_id: int):
        """Worker 协程处理主循环"""
        logger.info(f" Worker 协程 #{worker_id} 启动, 准备接受任务...", extra={"trace_id":f"WORKER-{worker_id}"})
        while self.is_running or not self.task_queue.empty():
            try:
                # 从队列中提取任务，设置 0.5s 超时以便检查 is_running 状态
                payload = await asyncio.wait_for(self.task_queue.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue

            # 处理任务
            result = await self._process_single_payload(payload)

            # 如果是严重错误或异常状态，送入死信队列保存死现场以备后续审计
            if result.status_code >= 500:
                await self.dead_letter_queue.put(result)

            self.task_queue.task_done()

        logger.info(f" Worker_id 协程 #{worker_id} 退出。", extra={"trace_id": f"WORKER-{worker_id}"})

    async def start(self):
        """启动微服务网关引擎"""
        self.is_running = True
        logger.info(f" 启动网关调度引擎 | Worker 并发数: {self.worker_concurrency} | 超时熔断值: {self.request_timeout}s")
        # 派生 Worker 协程池
        self.workers = [asyncio.create_task(self._worker_loop(i))
                        for i in range(self.worker_concurrency)]

    async def shutdown(self):
        """【优雅停机 (Graceful shutdown)】保障存量任务处理完后再退出"""
        logger.info(" 收到关机指令, 开始执行优雅停机流程...")
        # 1. 停止接收新任务循环标记
        self.is_running = False

        # 2. 等待队列中剩余的所有任务完成
        await self.task_queue.join()

        # 3. 取消所有的 Worker 任务
        for worker in self.workers:
            worker.cancel()

        await asyncio.gather(*self.workers, return_exceptions=True)
        logger.info(f" 关机完成！本次全生命周期累计成功处理业务: {self._processed_count} 项，死信队列残留异常记录: {self.dead_letter_queue.qsize()} 条。")

# ==============================================================================
# 实战测试用例逻辑（全面打爆网关：包含正常流量、攻击流量、超时流量、重放流量）
# ==============================================================================

async def main():
    engine = SafeAsyncGatewayEngine(worker_concurrency=3, request_timeout=1.0)
    await engine.start()

    now = time.time()

    # 构造多元化的模拟测试流量包
    raw_test_data =[ 
        # (ID, 偏移时间, 业务内容, 是否使用恶意签名)
        ("REQ-001", 0.0, "normal_user_profile_query", False),
        ("REQ-002", 0.0, "normal_order_checkout", False),
        ("REQ-003", 0.0, "slow_payload_test_timeout", False),     # 触发 504 超时
        ("REQ-004", 0.0, "malicious_sql_injection_test", False),  # 触发 500 异常捕获并送死信队列
        ("REQ-001", 0.0, "normal_user_profile_query", False),     # 触发防重放攻击 (与 REQ-001 ID 重复)
        ("REQ-005", -10.0, "replay_attack_expired_timestamp", False), # 触发时间戳失效 (过早的请求)
        ("REQ-006", 0.0, "tampered_data_attack", True),           # 触发签名篡改攻击 (401)
        ]

    # 添加大量并发数据测试限流器（Token 桶）
    for i in range(7, 12):
        raw_test_data.append((f"REQ-00{i}", 0.0, f"burst_traffic_{i}", False))

    print("\n" + "="*80)
    print(" [演练开始] 启动工业级异步微服务网关安全与高并发全测试")
    print("="*80 + "\n")

    # 提交测试流量包
    for req_id, time_offest, data, tamper in raw_test_data:
        ts = now + time_offest
        if tamper:
            sig = "bad_hacker_signature_999"
        else:
            sig = await engine.generate_signature(req_id, ts, data)

        payload = EncryptedRequestPayload(request_id=req_id,
                                          client_ip="192.168.1.105",
                                          timestamp=ts,
                                          data=data,
                                          signature=sig)
        await engine.submit_request(payload)
        await asyncio.sleep(0.05)  # 极短间隔快速冲刺

    # 给网络处理留足空间，然后执行优雅停机
    await asyncio.sleep(3.5)
    print("\n" + "="*80)
    await engine.shutdown()
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
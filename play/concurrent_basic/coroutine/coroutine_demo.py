"""
=============================================================================
项目名称: 工业级高并发多任务安全抓取与处理引擎
核心技术栈: Python, Gevent (猴子补丁, 协程池, 显式超时控制)
核心防御标准:
  1. 异常隔离 (Exception Isolation) - 单任务崩溃决不拖垮主进程
  2. 资源池化 (Resource Pooling) - 限制并发水位，防止系统内存撑爆
  3. 硬超时兜底 (Hard Timeouts) - 杜绝僵尸任务和无限挂起
  4. 深度注释 (Deep Commentary) - 架构意图与崩溃防护全记录
=============================================================================
"""

import gevent
from gevent import monkey

# =============================================================================
# 【架构笔记 01：猴子补丁 (Monkey Patching) 的执行时机与底层意义】 
# [为什么必须在最顶部执行?]
# Python 标准库（如 socket, time, select 等）底层都是同步阻塞的 IO。
# monkey.patch_all() 的本质，是在程序启动的最初一瞬间，用 Gevent 的非阻塞
# 异步 IO 版本“动态替换”掉标准库的阻塞版本。
# [防御警示]: 如果在 patch 之前引入了其他依赖库，或者在代码中途才打补丁，
# 会导致标准库已经被部分加载，从而引发底层 IO 切换失效，程序退化为同步阻塞。
# =============================================================================
monkey.patch_all()

import time
import random
from gevent.pool import Pool
from gevent import Timeout

# =============================================================================
# 【架构笔记 02：自定义业务异常体系】
# 
# 为什么要自定义异常类 (TaskExecutionError)?
# 在大型工程中，绝对不能盲目捕获所有 Exception。我们必须区分：
#   - 预期内的业务故障 (如数据格式错误、解析失败) -> 归入 TaskExecutionError 拦截并记录。
#   - 系统级或未知致命故障 (如内存溢出、空指针) -> 走通用异常兜底。
# 个人认为，这样才能在最后的盘点报告里精准统计失败原因。
# =============================================================================
class TaskExcutionError(Exception):
    """自定义业务异常: 用于隔离并明确记录协程内部发生的特定业务逻辑故障"""
    pass

class TaskEngine:
    """
    【架构笔记 03: 任务引擎核心类封装】
    
    采用面向对象设计，将配置参数（并发上限、超时时间）与运行状态（成功池、失败池）
    内聚在类内部，符合高内聚、低耦合的工业级标准。
    """
    def __init__(self, max_concurrency: int = 5, global_timeout: float = 3.0):
        """
        初始化工业级并发任务引擎
        
        :param max_concurrency: [支柱2 - 资源池化] 严格限制最大并发协程数量。
                                如果有 10000 个任务, Pool(5) 会将它们排队分批执行，
                                绝不会瞬间开启 10000 个协程导致内存和文件描述符 (FD) 撑爆。
        :param global_timeout: [支柱3 - 硬超时兜底] 单个任务运行的最大允许时间（秒）。
                                超过这个时间，无论任务进行到哪一步，都会被强制强行切断。
        """
        self.pool = Pool(max_concurrency)
        self.global_timeut = global_timeout

        # 结果容器：用于后续的盘点统计
        self.success_results = []
        self.failed_results = []

    def _safe_task_wrapper(self, task_id: int, task_func, *args, **kewargs):
        """
        =========================================================================
        【架构笔记 04: 全量防御包裹函数（核心防线）】
        Full defense wrapper: Exception Isolation & Hard Timeout handling.
        这是整个引擎中最关键的保护层。任何传入的外包任务，都必须经过这个函数的
        “三重安检”才能安全返回。
        
        安检流程:
        1. 计时开始
        2. 挂载 Timeout 上下文（硬超时防线）
        3. 执行具体业务函数
        4. 异常拦截与分类处理（异常隔离防线）
        =========================================================================
        """
        start_time = time.time()

        try:
            # 【防御机制：硬超时上下文管理器】
            # 当 with 内部的代码块运行时间超过 self.global_timeout 时，
            # Gevent 会主动向当前协程抛出一个 Timeout 异常，从而强行中断死循环或慢 IO。
            # 而硬超时兜底通过第二个参数注入 TaskExecutionError，超时自动转换异常
            # Hard Timeout with exception injection
            time_msg = f"任务强制超时 (超过设定阈值 {self.global_timeut}s)"
            with Timeout(self.global_timeut, TaskExcutionError(time_msg)):
                # 执行具体传入的业务逻辑（高阶函数回调机制）
                result = task_func(task_id, *args, **kewargs)

                # 计算耗时并安全记录成功状态
                elapsed = round(time.time() - start_time, 2)
                self.success_results.append({"task_id": task_id, "result": result, "elapsed": elapsed})
                print(f"[SUCCESS] 任务 {task_id} 顺利完成, 耗时: {elapsed}s, 结果: {result}")

        except TaskExcutionError as tee:
            # =================================================================
            # 【防御捕获 2：已知业务异常与超时转换异常拦截】
            # Exception Isolation for business & timeout errors
            # 捕获我们在业务中主动抛出的预期内故障。
            # =================================================================
            elapsed = round(time.time() - start_time, 2)
            self.failed_results.append({"task_id": task_id, "error": str(tee), "elapsed": elapsed})
            print(f"[WARN] 任务 {task_id} 被安全隔离: {tee}")

        except (KeyboardInterrupt, SystemExit):
            # =================================================================
            # 【架构警示 3：放行系统中断信号】
            # 绝对不能用普通的 'except Exception' 吞掉 KeyboardInterrupt（Ctrl+C）。
            # 必须向上冒泡，确保运维或开发者在紧急情况下可以随时安全退出程序，
            # 防止产生无法杀死的僵尸进程。
            # =================================================================
            raise

        except Exception as e:
            # =================================================================
            # 【防御捕获 4：未知异常兜底防线】
            # 捕获诸如 TypeError, KeyError 等一切未预料到的底层崩溃。
            # 确保即使某一个任务内部炸了，异常也被死死锁在本协程内，
            # 绝不会向外扩散污染主线程。
            # =================================================================
            elapsed = round(time.time() - start_time, 2)
            self.failed_results.append({"task_id": task_id, "error": f"未知底层崩溃: {str(e)}", "elapsed": elapsed})
            print(f"[ERROR] 任务 {task_id} 内部崩溃已被成功隔离: {str(e)}")

    def run_batch(self, task_list: list, task_func):
        """
        【架构笔记 05: 批量调度与并发同步】
        
        :param task_list: 待处理的任务 ID 列表或参数列表
        :param task_func: 实际执行的具体业务函数
        """
        print(f"--> [Engine Active] 提交的任务总数: {len(task_list)} | 协程池并发水位: {self.pool.size}")

        # 1. 列表推导式结合 pool.spawn：将每个任务分发给协程池异步调度
        # 注意：此时任务并没有瞬间全部执行完，而是受 pool 容量限制分批吞吐
        jobs = [self.pool.spawn(self._safe_task_wrapper, task_id, task_func)
                for task_id in task_list]

        # 2. 阻塞主进程：gevent.joinall 确保主程序必须等待池内所有协程彻底收尾
        # 才会向下执行打印统计报告，防止主线程提前退出导致子协程沦为孤儿。
        gevent.joinall(jobs)
        print("--> [Engine Done] 所有并发任务调度与收尾完毕。")

# =============================================================================
# 【模拟工业级业务函数】
# 
# 模拟真实世界中不稳定的网络请求或数据库查询。
# 故意夹杂正常延迟、超长延迟（触发硬超时）以及脏数据异常（触发隔离）。
# =============================================================================
def mock_network_fetch(task_id: int):
    """
    模拟不稳定的 IO 行为
    """
    # 随机选择一种运行结果（正常耗时、慢耗时触发超时、或者数据类型错误）
    delay =random.choice([0.5, 1.2, 3.5, "error_type"])

    # 模拟数据类型污染导致的意外奔溃
    if delay == "error_type":
        raise TypeError(f"接收到无法解析的非法脏数据格式 (Task {task_id})")

    # 模拟阻塞 IO：由于前面打了 monkey.patch_all()，
    # 这里的 time.sleep 不会阻塞整个 CPU，而是会触发 Gevent 自动让出 CPU 权，
    # 切换到其他并发协程执行！
    time.sleep(delay)
    return f"Data_Payload_{task_id}"

# =============================================================================
# 【主程序入口 (Entry Point)】
# =============================================================================
if __name__ == "__main__":
    # 实例化引擎：
    # - max_concurrency=3 : 最多同时跑 3 个协程（资源池化）
    # - global_timeout=2.0 : 任何任务超过 2 秒没做完，直接强制切断（硬超时兜底）
    engine =TaskEngine(max_concurrency=3, global_timeout=2.0)

    # 模拟 8 个并发任务输入
    tasks = list(range(101, 109))

    # 启动批量调度
    engine.run_batch(tasks,mock_network_fetch)

    # 打印最终的兵工厂盘点报告
    print("\n" + "="*50)
    print("【私密兵工厂 - 工业级盘点报告】")
    print(f"成功运行: {len(engine.success_results)} 个")
    print(f"失败/隔离: {len(engine.failed_results)} 个")
    print("失败明细归档:")
    for fail in engine.failed_results:
        print(f"  - 任务 {fail['task_id']}: {fail['error']} (耗时 {fail['elapsed']}s)")
    print("="*50)

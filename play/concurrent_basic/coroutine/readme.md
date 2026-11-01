# 【项目架构笔记】工业级高并发多任务安全抓取与处理引擎

* **项目代号**: `coroutine_demo`
* **核心技术栈**: Python, Gevent (Monkey Patching, Coroutine Pool, Hard Timeout Injection)
* **设计标准**: 防御性编程“四大支柱” (Exception Isolation, Resource Pooling, Hard Timeouts, Deep Commentary)

---

## 一、 核心架构设计意图

本项目的核心目标是构建一个**抗击打、高吞吐、绝对防爆裂**的异步并发任务调度引擎。在面对真实生产环境中不可预测的网络抖动、慢 IO 阻塞以及脏数据污染时，引擎必须具备自愈和隔离能力，决不能因单点故障导致整体崩溃。

---

## 二、 工业级防御“四大支柱”落地实现

### 1. 猴子补丁与非阻塞 IO (`Monkey Patching`)
* **实现机制**: 在程序启动之初执行 `gevent.monkey.patch_all()`。
* **架构意义**: 动态将标准库（如 `time`, `socket`）的同步阻塞调用替换为异步非阻塞 IO。单个协程在进入等待状态（如 `time.sleep`）时会自动让出 CPU 权限，实现单线程下的多任务高效并发。

### 2. 资源池化与流量截流 (`Resource Pooling`)
* **实现机制**: 引入 `gevent.pool.Pool(max_concurrency)`。
* **架构意义**: 严格限制并发水位线（如最大同时运行 3 个协程）。防止海量任务瞬间涌入导致内存溢出（OOM）或文件句柄耗尽。

### 3. 硬超时兜底与异常注入 (`Hard Timeouts & Exception Injection`)
* **实现机制**: 采用 `with Timeout(seconds, CustomException(...))` 机制。
* **架构意义**: 彻底解决原生 `Timeout` 触发时抛出 `BaseException` 导致无法被普通 `except` 捕获的痛点。一旦任务超时，Gevent 会自动将超时转换为预期的业务异常，实现精准拦截。

### 4. 异常隔离与防爆隔离墙 (`Exception Isolation`)
* **实现机制**: 全量包裹函数 `_safe_task_wrapper` 内置多重 `try...except` 分支。
* **架构意义**:
  - **业务/超时异常**: 统一捕获并归入失败明细。
  - **未知底层崩溃**: 锁死在当前协程内部，绝不外泄污染主线程。
  - **系统中断信号**: 显式放行 `KeyboardInterrupt` / `SystemExit`，杜绝僵尸进程。

---

## 三、 关键踩坑与演进复盘（Troubleshooting）

* **痛点问题**: 早期版本中使用原生的 `with Timeout(seconds):` 时，超时触发的底层 `Timeout` 属于 `BaseException`，绕过了常规的异常捕获网，导致超时任务“裸奔”退出，无法计入盘点报告。
* **终极解法**: 采用**异常注入模式**（传入第二个参数自定义异常类），让超时信号无缝转换为 `TaskExecutionError`，实现了预期异常与超时异常的统一收网。

---

## 四、 混沌测试与盘点报告验证（Chaos Testing Results）

在模拟 8 个并发任务（夹杂正常延迟、超长超时、脏数据类型错误）的压测中，系统表现出完美的收敛能力：
* **成功与隔离对齐**: 成功任务与失败/隔离任务总数严格闭环（例如：3 个成功 + 5 个被成功隔离的异常 = 总计 8 个任务）。
* **零孤儿协程**: 所有异常均被精准捕获并生成结构化盘点明细。

---
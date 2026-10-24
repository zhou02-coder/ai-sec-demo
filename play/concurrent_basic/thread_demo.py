import threading
import time

# ==================================================
# 工程化升级：OOP 封装线程安全计数器
# OOP Encapsulation：Thread-safe Counter Class
# 作用：消除全局变量，将状态、锁、业务逻辑封装在类内部
# ==================================================
class ThreadCounter:
    '''Thread-safe counter class, encapsulates shared state and mutex lock.
        线程安全计数器类, 封装共享状态与互斥锁，消除全局变量'''
    def __init__(self):
        self._count = 0   # 内部共享计数 / Internal shared counter
        self._lock = threading.Lock()    # 内部互斥锁 / Interanal mutex lock

    def reset(self):
        '''Reset counter to 0 / 重置计数器'''
        self._count = 0
    @property
    def count(self):
        '''Get current count value / 获取当前计数值'''
        return self._count

    def increment_unlocked(self):
        '''Increment without lock (for race condition demonstration)
            无锁自增 (仅用于演示资源竞争我呢提, 生产环境禁止使用)'''
        self._count += 1

    def increment_safe(self):
        '''Thread-safe increment with minium critical section (standard practice)
            线程安全自增 - 最小临界区 (工程标准写法)'''
        with self._lock:
            self._count += 1

    def batch_increment_big_lock(self, task_count: int):
        '''Big critical section: lock wraps the whole loop (for granularity)
            大临界区批量自增: 锁包住整个循环 (仅用于锁粒度性能对比)'''
        with self._lock:
            for _ in range(task_count):
                self._count += 1

    def risky_increment_demo(self):
        '''Demonstrate exception safety of "with lock"
            演示 with lock 在异常场景下的自动释放能力'''
        try:
            with self._lock:
                print("Lock acquired inside class, about to raise error...")
                raise ValueError("Simulated business exception")
        except ValueError as e:
            print(f" Exception caught: {e}")
            # 异常后再次尝试拿锁，验证无死锁
        print(" Trying to acquire lock again after exception...")
        with self._lock:
            print(" Success! Lock auto-released, no deadlock.")
            print(" 验证通过: 异常后锁自动释放, 无死锁风险")

# ========================================================================
# 工具函数：融合旧知识点 - 生成器构造任务队列
# Utility：Reuse generator knowledge to bulid memory-efficient task queue
# ========================================================================
def task_generator(task_count: int):
    '''Generate task ID sequence via generator, saves memory vs full list.'''
    for task_id in range(task_count):
        yield task_id

# ===============================
# 全局配置 / Global Config
# ===============================
TOTAL_TASKS = 1_000_000  #总任务量

# =================================================
# Demo 1：单线程基准测试 / Single Thread Benchmark
# 作用：建立性能与结果参照物
# =================================================
def demo_single_thread(counter:ThreadCounter):
    print("\n" + "="*60)
    print("Demo 1: Single Thread Benchmark / 单线程基准测试")
    print("="*60)
    counter.reset()
    start = time.time()

    for _ in task_generator(TOTAL_TASKS):
        counter.increment_unlocked()   # 单线程无竞争，无需锁
    cost = time.time() - start
    print(f"Final count: {counter.count}")
    print(f"Time cost:   {cost:.4f}s")
    return cost

# =========================================================
# Demo 2:多线程无锁 - 复现资源竞争
# Demo 2：Unlocked Multi-thread - Reproduce Race Condition
# =========================================================
def demo_race_condition(counter:ThreadCounter):
    print("\n" + "="*60)
    print("Demo 2: Race Condition (no lock) / 无锁资源竞争复现")
    print("="*60)
    counter.reset()
    per_thread =TOTAL_TASKS // 2

    def worker(work_count: int):
        for _ in task_generator(work_count):
            counter.increment_unlocked()   # 无保护修改共享变量
    start =time.time()
    t1 =threading.Thread(target=worker, args=(per_thread,))
    t2 =threading.Thread(target=worker, args=(per_thread,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    cost =time.time() -start
    print(f"Final count: {counter.count} (expected: {TOTAL_TASKS})")
    print(f"Time cost:   {cost:.4f}s")
    print("说明: 因资源竞争, 最终计数通常小于预期值")

# ===============================================
# Demo 3：join() 时序控制演示
# Demo 3：join() Timing Control Demonstration
# ===============================================
def demo_join_behavior(counter:ThreadCounter):
    print("\n" + "="*60)
    print("Demo 3: join() Timing Control / join 时序控制")
    print("="*60)
    counter.reset()

    def slow_worker():
        time.sleep(0.5)  #模拟耗时IO任务
        counter.increment_unlocked()
        counter.increment_unlocked()

    t =threading.Thread(target=slow_worker)
    start =time.time()

    t.start()
    # 无join：主线程直接往下走，子线程还未执行完成
    print(f"Before join: count = {counter.count}, time = {time.time()-start:.4f}s")

    t.join()  #主线程阻塞，等待子线程执行完毕
    print(f"After join: count = {counter.count}, time = {time.time()-start:.4f}s")
    print("核心结论: join只控制等待时序, 不能解决竞争问题")

# =====================================================
# Demo 4：互斥锁修复-最小临界区 (工程规范写法)
# Demo 4：Thread-safe Lock - Minimum Critical Section
# =====================================================
def demo_thread_safe(counter:ThreadCounter):
    print("\n" + "="*60)
    print("Demo 4: Thread Safe Lock (minimum critical section) / 互斥锁修复 - 最小临界区 (工程规范写法)")
    print("="*60)
    counter.reset()
    per_thread =TOTAL_TASKS // 2

    def worker(work_count: int):
            for _ in task_generator(work_count):
                counter.increment_safe()   # 每次自增单独加锁，临界区最小
    start =time.time()
    t1 =threading.Thread(target=worker, args=(per_thread,))
    t2 =threading.Thread(target=worker, args=(per_thread,))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    cost =time.time() -start
    print(f"Final count: {counter.count} (expected: {TOTAL_TASKS})")
    print(f"Time cost:   {cost:.4f}s")
    print("规范说明: 使用 with lock 上下文管理器, 异常场景也能自动释放锁")

# =================================================
# Demo 5：锁粒度性能对比
# Demo 5：Lock Granularity Performance Comparison
# =================================================
def demo_lock_granularity(counter:ThreadCounter):
    print("\n" + "="*60)
    print("Demo 5: Lock Granularity Comparison / 锁粒度性能对比")
    print("="*60)
    counter.reset()
    per_thread =TOTAL_TASKS // 2
    
    start =time.time()
    t1 =threading.Thread(target=counter.batch_increment_big_lock, args=(per_thread,))
    t2 =threading.Thread(target=counter.batch_increment_big_lock, args=(per_thread,))
        
    t1.start()
    t2.start()
    t1.join()
    t2.join()
        
    cost =time.time() -start
    print(f"Big lock time: {cost:.4f}s (almost serial execution)")
    print("工程原则: 只把共享资源操作放入锁内, IO、耗时代码尽量放锁外")
    print("补充: 大临界区并发度极低, 仅适合任务量极小, 加锁开销敏感的场景")

# ==========================================
# Demo 6：锁异常安全验证
# Demo 6：Lock Excption Safety Verifiction
# ==========================================
def demo_exception_safety(counter:ThreadCounter):
    print("\n" + "="*60)
    print("Demo 6: Lock Granularity Comparison / 锁粒度性能对比")
    print("="*60)
    counter.risky_increment_demo()
    print('风险提示: 手动 acquire/release 写法在此场景会造成永久死锁')

# =================================
# 主入口 / Main Entry
# =================================
if __name__ =="__main__":
    print("="*60)
    print("Python Thread Comprehensive Demo (OOP Edition)")
    print("Python 多线程综合实战 (OOP 封装版)")
    print("基础知识点: 线程创建、共享资源、资源竞争、join、互斥锁")
    print("工程升级: OOP封装消除全局变量, 状态与锁内聚")
    print("="*60)

    # 全局仅实例化一个计数器对象，替代原全局变量
    counter = ThreadCounter()
    demo_single_thread(counter)
    demo_race_condition(counter)
    demo_join_behavior(counter)
    demo_thread_safe(counter)
    demo_lock_granularity(counter)
    demo_exception_safety(counter)

    print("\n" + "="*60)
    print("All demos finished. / 全部演示完毕")
    print(" 1. 裸 Thread + start/join 是并发原理根基, 必须吃透")
    print(" 2. join 只管时序等待, 不解决数据竞争问题")
    print(" 3. with lock 是工程标准写法, 天然防死锁")
    print(" 4. 临界区越小, 并发性能越好; 锁只保护共享资源")
    print(" 5. OOP 封装消除全局变量, 状态内聚, 更易扩展与维护")
    print("="*60)
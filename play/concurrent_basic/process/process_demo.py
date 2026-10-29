"""
Process Core Knowledge Practical Exercises (Architect Edition with Bilingual Comments)
   进程核心知识点实战练习合集 (架构师双语注释版)
   涵盖知识点 / Covered Topics: 
   - Process Syntax & Lifecycle / 进程语法结构与生命周期
   - Safe IPC (Queue / pipe + Deadlock Prevention) / 进程间安全通信与死锁防范
   - Parallel Computing & Result Aggregation / 多进程并行计算与结果汇总
"""

import multiprocessing
import os
import random
import time

# ===================== 练习1 辅助函数 / Exercise 1 Helper =====================
def ex1_worker_task(name: str, delay: int) -> None:
    """
    Child process worker: print process info and simulate time-consuming task.
    子进程工作函数: 打印进程信息并模拟耗时任务。
    """
    current_process = multiprocessing.current_process()
    print(f"[子进程启动 / Child Started] Name: {name}, PID: {current_process.pid}, System Name: {current_process.name}")
    time.sleep(delay)
    print(f"[子进程结束 / Child Ended] Task {name} completed successfully.")

# ===================== 练习2 辅助函数 / Exercise 2 Helper =====================
def ex2_state_worker() -> None:
    """
    current = multiprocessing.current_process()
    进程状态观测工作函数。
    """
    current = multiprocessing.current_process()
    print(f"[运行态 / Running] Process {current.pid} enters running state, starting computation.")
    for i in range(3):
        print(f"Calculating... Round {i+1} / 计算中... 第{i+1}轮")
        time.sleep(0.5)

    print(f"[阻塞态 / Blocked] Simulating I/O wait, pausing for 1 second / 模拟IO等待, 暂停1秒")
    time.sleep(1)

    print(f"[运行态 / Running] I/O finished, back to running state.")
    print(f"[终止态 / Terminated] Task completed, process exiting.")

# ===================== 练习3 辅助函数 / Exercise 3 Helper =====================
def ex3_producer(queue: multiprocessing.Queue, producer_name: str, count: int, consumer_count: int,) -> None:
    """
    Producer Process: Puts data into the queue and sends sentinel values (Poison Pills)
    to match the excat number of consumers, preventing deadlock.
    生产者进程: 往队列中放入数据, 并发送与消费者数量匹配的哨兵值 (结束信号), 防止死锁。
    """
    for i in range(count):
        time.sleep(random.uniform(0.1, 0.3))
        data = f"{producer_name}-Data-{i+1}"
        queue.put(data)
        print(f"[{producer_name}] Produced: {data}")
    # Architectural Fix：Send exact number of None sentinels for each consumer
    # 架构修复：为每个消费者精准发送对应数量的 None 哨兵
    for _ in range(consumer_count):
        queue.put(None)
    print(f"[{producer_name}] Production finished, sent {consumer_count} termination sentinels.")

def ex3_consumer(queue: multiprocessing.Queue, consumer_name: str) -> None:
    """
    Consumer Process: Retrieves data from the queue until receiving the sentinel.
    消费者进程: 从队列中获取数据, 直到收到哨兵信号为止。
    """
    while True:
        data = queue.get()
        if data is None:
            print(f"[{consumer_name}] Received sentinel, exiting consumption.")
            break
        time.sleep(random.uniform(0.2, 0.4))
        print(f"[{consumer_name}] Consumed: {data}")

# ===================== 练习4 辅助函数 / Exercise 4 Helper =====================
def ex4_pipe_worker(conn, worker_name: str) -> None:
    """
    Pipe Worker Process: Utilizes built-in process safety of Pipe without external locks,
    preventing blocking deadlock scenarios.
    管道工作进程: 利用 Pipe 内置的进程安全性, 不加额外外层锁, 防止阻塞死锁场景。
    """
    for i in range(3):
        # Read from pipe (block until data arrives) / 从管道读取（阻塞直到数据到达）
        msg =conn.recv()
        print(f"[{worker_name}] Received: {msg}")

        time.sleep(0.2)

        reply = f"Reply-{i+1}: Acknowledged [{msg}]"
        # Send back to main process / 发回主进程
        conn.send(reply)
        print(f"[{worker_name}] Sent: {reply}")
    
    conn.close()

# ===================== 练习5 辅助函数 / Exercise 5 Helper =====================
def ex5_calculate_square_sum(start: int, end: int, result_queue: multiprocessing.Queue) -> None:
    """
    Parallel Task: Calculate the sum of squares within a specific numeric range.
    并行任务: 计算指定数值区间内的平方和。
    """
    current_pid = multiprocessing.current_process().pid
    print(f"Process {current_pid} started, computing range [{start}, {end}]")

    total = 0
    for num in range(start, end + 1):
        total += num**2
        time.sleep(0.01)

    result_queue.put((start, end, total))
    print(f"Process {current_pid} completed, result: {total}")

# ===================== 练习1：基础语法与核心方法属性 =====================
def exercise1_basic_syntax() -> None:
    print("\n" + "=" * 60)
    print("Exercise 1: Basic Process Syntax & Core Methods/Attributes")
    print("练习1: 进程基础语法与核心方法、属性实操")
    print("=" * 60 + "\n")

    print("=== Main Process Starts / 主进程开始执行 ===")
    main_process = multiprocessing.current_process()
    print(f"Main Process PID: {main_process.pid}")

    # 1. Create a Process object (New State) / 创建进程对象（新建态）
    p1 =multiprocessing.Process(target=ex1_worker_task, args=("Worker-1", 2), name="Custom=Worker1")
    print(f"\n Attributes after process creation / 进程创建后属性:")
    print(f"Process Name: {p1.name}")
    print(f"Process PID (None before start): {p1.pid}")
    print(f"Is Alive: {p1.is_alive()}")
    print(f"Is Daemon: {p1.daemon}")

    # 2. Start the process (Ready -> Running State) / 启动进程（就绪 -> 运行态）
    p1.start()
    print(f"\n After calling start() / 调用Start()后:")
    print(f"Process PID: {p1.pid}")
    print(f"Is Alive: {p1.is_alive()}")

    # 3. Block and wait for child process to finish / 阻塞等待子进程结束
    p1.join()
    print(f"\n After calling join() / 调用join()后:")
    print(f"Is Alive: {p1.is_alive()}")
    print(f"Exit Code: {p1.exitcode}")
    print("=== Main Process Ends / 主进程执行结束 ===")

# ===================== 练习2：进程状态生命周期观测 =====================
def exercise2_state_observation() -> None:
    print("\n" + "=" * 60)
    print("Exercise 2: Process Lifecycle State Observation")
    print("练习2: 进程生命周期状态观测实验")
    print("=" * 60 + "\n")

    # New State / 新建态
    p = multiprocessing.Process(target=ex2_state_worker, name="State-Test")
    print(f"[New State] Process created, not started. Alive: {p.is_alive()}")

    # Ready & Running State / 就绪与运行态
    p.start()
    print(f"[Ready/Running] Process started, waiting for CPU scheduling. Alive: {p.is_alive()}")

    # Termination State / 终止态
    p.join()
    print(f"[Terminated] Process finished. Alive: {p.is_alive()}, Exit Code: {p.exitcode}")

# ===================== 练习3：Queue安全通信（生产者-消费者） =====================
def exercise3_queue_communication() -> None:
    print("\n" + "=" * 60)
    print("Exercise 3: Safe IPC via Queue (Producer-Consumer Pattern)")
    print("练习3: Queue进程间安全通信(生产者-多消费者模型）")
    print("=" * 60 + "\n")

    shared_queue =multiprocessing.Queue(maxsize=10)
    consumer_count = 2

    p_prod = multiprocessing.Process(target=ex3_producer, args=(shared_queue, "Producer-A", 8, consumer_count),)
    p_cons1 = multiprocessing.Process(target=ex3_consumer, args=(shared_queue, "Consumer-1"))
    p_cons2 = multiprocessing.Process(target=ex3_consumer, args=(shared_queue, "Consumer-2"))

    p_prod.start()
    p_cons1.start()
    p_cons2.start()

    p_prod.join()
    p_cons1.join()
    p_cons2.join()

    print("\n All processes finished safety. Communication completed.")

# ===================== 练习4：Pipe双向安全通信 =====================
def exercise4_pipe_communication() -> None:
    print("\n" + "=" * 60)
    print("Exercise 4: Duplex Safe Communication via Pipe (Deadlock-Free)")
    print("练习4: Pipe 双向安全通信(无死锁风险版）")
    print("=" * 60 + "\n")

    parent_conn, child_conn = multiprocessing.Pipe(duplex=True)

    p = multiprocessing.Process(target=ex4_pipe_worker, args=(child_conn, "Worker-Pipe"))
    p.start()

    for i in range(3):
        send_msg = f"Main-Instruction-{i+1}"
        parent_conn.send(send_msg)
        print(f"[Main Process] Sent: {send_msg}")

        reply =parent_conn.recv()
        print(f"[Main Process] Received Reply: {reply}")
    
    p.join()
    print("\n Pipe communication closed.")

# ===================== 练习5：综合并行计算实战 =====================
def exercise5_comprehensive_parallel() -> None:
    print("\n" + "=" * 60)
    print("Exercise 5: Comprehensive Practice - Parallel Computing & Aggregation")
    print("练习5:综合实战 - 多进程并行计算与结果安全汇总")
    print("=" * 60 + "\n")

    total_range = 100
    process_num = 4
    chunk_size = total_range // process_num

    result_queue = multiprocessing.Queue()
    processes = []

    for i in range(process_num):
        start = i * chunk_size + 1
        end =((i+1) * chunk_size if i != process_num - 1 else total_range)
        p =multiprocessing.Process(target=ex5_calculate_square_sum, args=(start, end, result_queue),)
        processes.append(p)
        p.start()
        print(f"Spawned Process PID: {p.pid}, Range:[{start}, {end}]")

    print("\n=== Process Runtime Monitoring / 进程运行状态监控 ===")
    while any(p.is_alive() for p in processes):
        alive_count = sum(1 for p in processes if p.is_alive())
        print(f"Active Processes: {alive_count}/{process_num}")
        time.sleep(0.3)

    for p in processes:
        p.join()

    grand_total = 0
    print("\n=== Result Aggregation / 结果汇总 ===")
    while not result_queue.empty():
        start, end, res = result_queue.get()
        print(f"Range [{start}, {end}] Sum of Squares: {res}")
        grand_total += res

    print(f"\n Total Sum (1~{total_range}): {grand_total}")
    print("All tasks completed successfully.")

# ===================== 主菜单入口 / Main Menu Entry =====================
def main() -> None:
    print("=" * 60)
    print("Process Practice Demo (Architect Bilingual Edition)")
    print("进程实战练习合集 | 架构师双语注释版")
    print("=" * 60)
    print("1. Basic Process Syntax & Methods / 进程基础语法与核心方法属性")
    print("2. Process Lifecycle States / 进程生命周期状态观测实验")
    print("3. Queue IPC (Producer-Consumer) / Queue进程间安全通信(生产者-多消费者)")
    print("4. Pipe Duplex Communication / Pipe双向安全通信")
    print("5. Parallel Computing & Aggreation / 综合实战: 多进程并行计算与结果汇总")
    print("0. Exit Program / 退出程序")
    print("=" * 60)

    while True:
        choice = input("\n Enter choice (0-5) / 请输入练习编号(0-5): ").strip()
        if choice == "0":
            print("Exiting program. Goodbye! / 退出程序。")
            break
        elif choice == "1":
            exercise1_basic_syntax()
        elif choice == "2":
            exercise2_state_observation()
        elif choice == "3":
            exercise3_queue_communication()
        elif choice == "4":
            exercise4_pipe_communication()
        elif choice == "5":
            exercise5_comprehensive_parallel()
        else:
            print("Invalid input, please enter 0-5 / 输入无效, 请输入0-5之间的数字。")

if __name__ == "__main__":
    main()

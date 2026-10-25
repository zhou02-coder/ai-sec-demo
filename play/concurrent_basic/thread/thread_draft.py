# 线程 
# 线程之间共享资源(全局变量)
from threading import Thread, Lock
import time 
def step_1():
    print("->[步骤1] 开始准备数据...")
    #time.sleep 模拟应该需要等待2秒的操作(比如读取文件)
    time.sleep(1)
    print("[步骤1] 完成! ")

def step_2():
    print("->[步骤2] 开始准备数据...")
    time.sleep(1)
    print("[步骤2] 完成! ")
print("=== 主线程 mainthread 开始执行 ===")
step_1()
step_2()
print("=== 程序结束 ===")

import threading

def worker_task():
    print("➜ [子线程] 开始在后台干活（模拟耗时 2 秒）...")
    # 子线程内部的阻塞（耗时操作）
    time.sleep(2)
    print("✔ [子线程] 活干完了！")

if __name__ == "__main__":
    print("=== 主程序开始 ===")
    
    # 1. 创建线程对象（指定它去执行 worker_task 函数）
    t = threading.Thread(target=worker_task, name="MyWorkerThread")
    
    # 2. 调用 start()：点火发射！
    # 此时操作系统会启动一个新线程去跑 worker_task。
    # 关键点：start() 是“非阻塞”的，主线程发完命令后会立刻往下走，不会在这里傻等。
    t.start()
    
    print("🚀 [主线程] 我已经发射了子线程，我不等它，我自己先往下走了！")
    
    # ----------------------------------------------------
    # 3. 关键点来了：调用 join() 引发“主线程阻塞”！
    # 如果没有这一行，主程序可能打印完上面那句就直接结束了。
    # 有了这一行，主线程会在这里“强行卡住（阻塞）”，
    # 死死盯着子线程 t，直到子线程打印完“活干完了！”，主线程才被放行！
    # ----------------------------------------------------
    print("⏳ [主线程] 现在我调用 t.join()，我必须在这里等子线程收工才能走...")
    t.join()
    
    print("=== [主线程] 子线程已经结束，主程序顺利收官！===")
    
# 资源竞争，共享内存
import threading
a = 0
b = 1000000
# 1. 实例化真正的锁对象（带括号！）
lock = threading.Lock()

def add():
    global a
    with lock:
        for _ in range(b):
        # 2. 使用 with 上下文管理器：
        #    进入 with 自动 acquire()，出了 with 哪怕报错也绝对自动 release()！
            a += 1
    print("第一次线程干完了! 当前累计值 a =", a)

def add2():
    global a
    with lock:
        for _ in range(b):
            a += 1
    print("第二次线程干完了! 当前累加值 a =", a)

if __name__ == "__main__":
    first = threading.Thread(target=add)
    second = threading.Thread(target=add2)

    first.start()
    #first.join()
    second.start()
    #second.join()

    print(f"✔ 完美精准的最终结果 a = {a}")

# 多任务、多线程
# 进程：是操作系统进行资源分配的基本单位，每打开一个程序里面至少就有一个进程
# 线程：是cpu调度的基本单位，每一个进程里面至少就有一个线程，这个线程通常就是我们说的主线程
# 一个进程默认有一个线程，进程里面可以创建多个线程，线程是依附在进程里面的，没有进程就没有线程
# 导入线程模块：import threading


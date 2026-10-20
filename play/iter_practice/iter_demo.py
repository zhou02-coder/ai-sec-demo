from collections.abc import Iterable, Iterator
import sys
import time

# ==============================================
# 模块一：可迭代对象 & 迭代器 底层协议实现
# Core：区分 Iterable（可迭代对象）/ Iterator（迭代器对象）
# 补充视频未讲：迭代器一次性消耗、可迭代对象可重复迭代核心原理
# ==============================================
class EvenIterator:
    """自定义偶数迭代器(标准迭代器)
        Custom Even number Iterator (Standard Iterator)
        满足迭代器协议:同时实现 __iter__() 和 __next__()
        特性:单次迭代,遍历完毕立即耗尽,无法二次使用"""
    def __init__(self, start, end):
        # 初始化遍历起始，结束边界
        # Initialize traversal start and end boundary
        self.current = start if start % 2==0 else start + 1
        self.end = end

    def __iter__(self):
        # 迭代器固定规则：__iter__() 方法必须返回自身
        # Interator fixed rule: the __iter__() method must return itself
        return self

    def __next__(self):
        # 逐次生成数据，越界时抛出 StopIteration 异常
        # Generate data step by step, rasie exceprtion when out of bounds
        if self.current > self.end:
            raise StopIteration
        res=self.current
        self.current += 2
        return res

class EvenRange:
    """自定义偶数可迭代对象(标准Interable)
        Custom Even number Iterable (Standard Iterable)
        满足可迭代对象协议:实现 __iter__(), 不实现__next__()
        特性:每次迭代生成全新迭代器, 支持无限次重复遍历"""
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __iter__(self):
        # 每次迭代返回新的迭代器实例，保证可重复迭代
        # Return a new iterator instance for each iteration
        return EvenIterator(self.start, self.end)

# ==============================================
# 模块二：生成器函数 高阶实战
# Core：yield暂停机制 + send/throw/close 生产级三大高阶方法
# 补充视频未讲：生成器本质=自动实现协议的迭代器
# ==============================================
def interactive_counter(start=0):
    """交互式计数器生成器函数
        Interactive Counter generator function
        支持: 外部传值重置、外部抛异常、主动关闭资源管理"""
    count = start
    while True:
        try:
            # yield 暂停函数、返回值、接收外部传入数据
            # yield pause function, return value, receive external data 
            reset_val = yield count
            # 接收send()传入的值，实现重置功能
            if reset_val is not None:
                count = reset_val
            else:
                count += 1
        except ValueError:
            # 捕获外部throw()抛出的异常
            print(f"[Generator Catch] 捕获 ValueError 异常, 重置计数器为 0")
            count = 0
        except GeneratorExit:
            # 捕获close()关闭信号，用于资源收尾
            print(f"[Generator Exit] 生成器被关闭，进行资源清理...")
            return  # 退出生成器函数，触发 StopIteration 异常

# ==============================================
# 模块三：生成器表达式 vs 列表推导式 性能基准测试
# Core：生成器表达式惰性求值 vs 列表推导式立即求值
# 补充视频未讲:工程选型标准、内存溢出OOM核心规避方案
# ==============================================
def performance_compare():
    '''百万级数据下内存、速度双维度对比测试
    Performance comparison: memory & speed
    under million-level data'''
    data_size=1_000_000

    # 1. 列表推导式：立即求值，全量占用内存
    start=time.time()
    list_data=(x*3 for x in range(data_size))
    list_time=time.time() - start
    list_mem=sys.getsizeof(list_data) / 1024 / 1024

    # 2. 生成器表达式：惰性求值，仅保存执行逻辑
    start=time.time()
    gen_data=(x*3 for x in range(data_size))
    gen_time=time.time() - start
    gen_men=sys.getsizeof(gen_data) / 1024 / 1024

    # 输出对比结果
    print("===== 列表推导式 VS 生成器表达式 性能对比 =====")
    print(f"列表推导式 | 耗时:{list_time:.4f}s | 内存:{list_mem:.2f}MB")
    print(f'生成器表达式 | 耗时:{gen_time:.4f}s | 内存:{gen_men:.6f}MB')
    print('惰性求值核心: 生成器不预存数据, 迭代时即时计算')

    # 验证生成器一次性消耗特性
    print("\n===== 生成器单次消耗验证 =====")
    print(next(gen_data), next(gen_data), next(gen_data))

# =========================================================
# 模块四：工业级实战 | 大文件流式读取(解决OOM内存溢出)
# Core: 生成器真实业务落地场景
# 补充视频wanquan未涉及：企业日志分析、超大文件处理标准写法
# =========================================================
def read_big_file(file_path):
    '''超大文件逐行读取生成器
        Read huge file line by line(stream reading)
        无论文件1G/10G, 内存仅占用单行数据, 杜绝OOM'''
    with open(file_path,"r", encoding="utf-8") as f:
        for line in f:
            yield line.strip()

def count_error_log(file_path):
    '''统计日志中ERROR错误行数'''
    error_count=0
    for line in read_big_file(file_path):
        if "ERROR" in line:
            error_count += 1
    return error_count

# ========================================
# 统一程序入口 | 按需开启测试(互不冲突)
# ========================================
if __name__=="__main__":
# 测试模块一：迭代器 & 可迭代对象
    #print("===== 模块一测试: 迭代器与可迭代对象 ======")
    #it=EvenIterator(0,10)
    #print("迭代器第一次遍历: ", list(it))
    #print("迭代器第二次遍历(已耗尽): ", list(it))
    #er=EvenRange(0,10)
    #print("可迭代对象第一次遍历: ", list(er))
    #print("可迭代对象第二次遍历: ", list(er))
    #print(f"Iterator校验: {isinstance(it, Iterator)}")
    #print(f"Iterator校验: {isinstance(er, Iterator)}")

# ============== 测试模块二：高阶生成器 ==============
    #print("\n===== 模块二测试: 高阶生成器 =====")
    #g = interactive_counter(5)
    #print(next(g))
    #print(next(g))
    #print(next(g))
    #print(g.throw(ValueError))
    #g.close()

# ======== 测试模块三：性能对比 ========
    #print("\n===== 模块三测试: 性能对比 =====")
    #performance_compare()

# ======== 测试模块四：大文件实战 ========
    print("\n===== 模块四测试: 大文件流式处理 =====")
    # #生成模拟10万行日志文件
    with open("big_log.log", "w", encoding="utf-8") as f:
        for i in range(100000):
            if i % 50 == 0:
                f.write(f"ERROR: Line {i} Runtime Error\n")
            else:
                f.write(f"INFO: Line {i} Normal Log\n")
    total_error=count_error_log("big_log.log")
    print(f"日志ERROR总行数: {total_error}")

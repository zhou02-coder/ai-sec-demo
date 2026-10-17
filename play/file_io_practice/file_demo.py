# 导入依赖模块 Import required modules
import time
import os  #进阶任务使用 Used for advanced tasks
from os.path import exists
# ----------------------
# 1. 日志写入函数 Log write function
# 参数：message；level，默认INFO
# ----------------------
def write_log(message:str,level:str='INFO') -> bool:
    """追加写入日志到app_log.txt,使用a追加模式,不会覆盖原有内容
    Append log to app_log.txt in append mode, old content will NOT be overwritten.
    param message:日志文本内容| Log message content
    param level: 日志级别 INFO/WARN/ERROR,用于区分日志类型| Log level
    Return True on success, False on failure"""
    # 使用strfttime格式化时间，生成标准化时间字符串
    # Purpose：统一日志时间格式，方便后续检索日志
    log_time=time.strftime("%Y-%m-%d %H:%M:%S")
    # 拼接完整日志行，末尾增加换行符\n,每条日志单独占一行
    # Purpose：每条日志独立一行，逐行读取时可以正常分割
    log_line=f"[{log_time}] [{level}] {message}\n"
    try:
        # with：上下文管理器打开文件，a=追加模式，显式指定utf-8
        # Why use with：代码执行结束自动调用close()，防止忘记关闭文件造成的资源泄漏
        # Why encoding='utf-8':Windows系统默认GBK，不指定会中文代码，生产代码强制写编码
        with open("app_log.txt", 'a', encoding="utf-8") as f:
            #将拼接好的日志字符串加入文件
            f.write(log_line)
            # tell()获取当前文件指针的字节位置，写入完成后指针停在文件末尾
            # Purpose：直观看到写入后指针位置，理解文件指针概念
            print(f'写入完成,当前指针位置 | Write finished, pointer pos:{f.tell()}')
        return True
    # 捕获权限不足异常：没有权限创建/修改文件时触发
    except PermissionError:
        print("[ERROR] 无文件写入权限 | No write permission to the file")
        return False
    #捕获其他所有IO相关异常
    except Exception as e:
        print(f"[ERROR] 日志写入失败 | Log write failed:{e}")
        return False
# --------------------
# 2. 逐行读取日志函数 Read log line by line
# --------------------
def read_log() ->bool:
    """逐行读取日志文件,采用readline()循环读取,适合超大日志文件
    Read log line by line. Avoid loading entire file into memory for large log"""
    try:
        with open("app_log.txt","r",encoding="utf-8") as f:
            print("\n===== 日志内容 | Log Content =====")
        # while循环持续读取单行
            while True:
            # readline()读取一行，包含末尾换行符
                line=f.readline()
                # 如果读到空字符串，代表到达文件末尾，推出循环
                # Important：文件末尾readline返回""空字符串，不是None
                if not line:
                    break
                # strip()去除首尾换行/空格，美化打印输出
                print(line.strip())
        return True
    except FileExistsError:
        print("[ERROR] 日志文件不存在 | Log file not found, please write log first")
        return False
    except FileNotFoundError:
        print("[ERROR] 文件编码错误, 不是UTF-8格式 | Encoding mismatch")
        return False
# -------------------
# 3. 文件指针操作演示 File pointer operation demo
# -------------------
def test_file_pointer() -> None:
    """演示seek()移动文件指针、tell()获取指针位置
    Demonstrate seek() move pointer and tell() get pointer position
    Note: seek偏移单位是字节, 不是字符! 中文utf8一个汉字3字节, 偏移汉字容易乱码"""
    print("\n===== 文件指针测试 | File Pointer Test =====")
    try:
        with open("app_log.txt","r", encoding="utf-8") as f:
        # tell()查询当前文件指针位置
            print(f"初始指针位置 | Initial position: {f.tell()}")
        # seek(offset, whence), whence=0 代表从文件开头计算偏移
        # 向后移5个字节
            f.seek(5,0)
            print(f"偏移5字节后指针位置 | After seek(5): {f.tell()}")
        # 读取3个字符
            content=f.read(3)
            print(f"读取3字符内容 | Read 3 chars: {content}")
        # seek(0,0) 将指针重置回到文件最开头
            f.seek(0,0)
            print(f"读取后指针位置 | Reset pointer to start: {f.tell()}")
    except FileNotFoundError:
        print("[ERROR] 请先输入日志, 再执行指针测试 | Write log before pointer test")

# -----------------------------
# 进阶任务（os模块）Advanced Task
# -----------------------------
def os_file_check():
    """使用os模块: 查看当前目录、检查文件是否存在、列出txt文件
    Use os module to check path and list text files"""
    print("\n===== OS模块文件检查 | OS File Check =====")
    # 获取当前程序运行的文件夹路径
    current_dir=os.getcwd()
    print(f"当前工作目录 | Current working dir: {current_dir}")

    #判断日志文件是否存在
    log_file_path="app_log.txt"
    if exists(log_file_path):
        print(f"{log_file_path} 存在 | File exists")
    else:
        print(f"{log_file_path} 不存在 | File not exists")

    #遍历当前目录，筛选所有txt后缀文件
    print("当前目录下txt文件:")
    for filename in os.listdir(current_dir):
        if filename.endswith(".txt"):
            print(f"- {filename}")
 # ----------------------
 # 主程序入口 Main entry
 # ----------------------
if __name__=="__main__":
    # 写入测试日志
    write_log("程序启动完成", "INFO")
    write_log("这是一条普通测试日志", "INFO")
    write_log("警告: 磁盘剩余空间不足", "WARN")

    #读取全部日志
    read_log()
    # 文件指针测试
    test_file_pointer()
    # os模块进阶功能
    os_file_check()
    

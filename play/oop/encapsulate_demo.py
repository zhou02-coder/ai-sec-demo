#-*-coding:utf-8 -*-
#文件:encapsulate_demo.py
#学习知识点:封装（私有属性）,__del__析构函数
#用途:跟着视频敲基础示例,理解核心语法
#记录:课堂练习,拆分小测试代码
class Person:
    def __init__(self):
        print('我是__init__()')
    def __del__(self):
        print('被销毁了')
p=Person()
del p     #删除这个p对象
#del p语句执行的时候，内存会被立即回收，会调用对象本身的__del__()方法
print('这是最后第二行代码')
print('这是最后一行代码')
#正常运行时，不会调用__del__(),对象执行结束之后，系统会自动调用
#__del__()主要是表示该程序块或者函数块就全部执行结束。
class Person2:
    name='Jmaes'  #类属性
    __age=28      #隐藏属性
    def introduce(self):    #实例方法
        Person2.__age=25    #修改隐藏属性
        print(f'{Person2.name}的年龄是{Person2.__age}')
        #在实例方法中访问类属性和隐藏属性
pe=Person2()
print(pe.name)
pe.introduce()

#隐藏方法
class Man:
    def __play(self):    #隐藏方法
        print('玩手机')
    def funa(self):      #正常普通的实例方法
        print('平平无奇的实例方法')
        self.__play()
ma=Man()
ma.funa()

#私有方法
class Girl:
    def _buy(self):
        print('整天买买买')
girl=Girl()
girl._buy()
#__init__()和__new__()
#__new__()：object基类提供的内置的静态方法
#作用：在内存中为对象分配空间；以及返回对象的引用
class Test(object):
    def __init__(self):
        print('这是__init__()')
    def __new__(cls):
        print('我是__new__()')
        #对父类方法进行扩展：super().方法名()
        re=super().__new__(cls)     #方法重写，re里面保存的是实例对象的引用
        return re
te=Test()
class Person(object):
    def __new__(cls,*args,**kwargs):
        print('这是new方法') 
        super().__new__(cls)
        print('返回值:',super().__new__(cls))
        return super().__new__(cls)
    def __init__(self,name):
        self.name=name        
        print('名字是:',self.name)
pe=Person('xiaoming')
print(pe)

#单例模式
#一个特殊的类，这个类只存在一个对象
class Singleton(object):
    #记录第一个被创建的对象的引用
    obj=None    #类属性
    def __new__(cls,*args,**kwargs):
        print('这是__new__()方法')
        #判断类属性是否为空
        if cls.obj==None:
            cls.obj=super().__new__(cls)
        return cls.obj
    def __init__(self):
        print('我是__init__()')
s=Singleton()
print('s:',s)
s2=Singleton()
print('s2:',s)

#通过导入模块实现单例模式
from poly_draft import te as te01
from poly_draft import te as te02
print(te01,id(te01))
print(te02,id(te02))

#魔法方法
#1.__doc__() 类的描述信息
class A(object):
    '''人类---类的描述信息'''  #三引号，无论单双
    pass
print(A.__doc__)

#2.__module__:表示当前操作对象所在的模块
#3.__class__:表示当前操作对象所在的类
import poly_draft
b=poly_draft.B()
print(b)
b.funa()
print(b.__module__)  #输出所在的模块
print(b.__class__)   #输出所在的类

#4.__str__(): 对象的描述信息
class C:
    def __str__(self):
        return '这里是str的返回值'   #必须要有返回值，并且一定是字符串类型
c=C()
print(c)

#5.__del__():析构函数，在程序结束时候会调用，或者是删除某个对象的时候也会被调用
#6.__call__():使一个实例对象成为一个可调用对象，就像函数一样可以调用
def func():
    print('测试是否为可调用对象')
func()
print(callable(func))
class D:
    def __call__(self, *args, **kwds):
        print('这是__call__()')
d=D()
d()
print(callable(d))
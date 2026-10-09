#实例属性，格式：self.属性名
class Person():  #类名
    name='zhouyuhao'      #类属性
    def introduce(self):  #实例方法
        print('我是实例方法')
        print(f'{Person.name}的年龄:{self.age}')
pe=Person()
pe.age=25     #动态添加实例属性
pe.introduce()
#构造函数
class Test():
    def __init__(self):
        print('这是__init__()函数')
te=Test()
class Person1():
    def __init__(self,name,age,height):
        self.name=name  #实例属性
        self.age=age
        self.height=height
    def play(self):
        print(f'{self.name}在玩游戏')
    def introduce1(self):
        print(f'{self.name}的年龄是{self.age},身高是{self.height}cm')
pe2=Person1('bingbing',20,170)
pe2.play()
pe2.introduce1()
pe3=Person1('ziyi',22,168)
pe3.play()
pe3.introduce1()
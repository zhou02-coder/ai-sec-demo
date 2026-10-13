#多态
class Animal(object):    #父类：动物类
    def shout(self):
        print('动物会叫')
class Cat(Animal):       #子类：猫类
    def shout(self):
        print('小猫喵喵喵')
class Dog(Animal):        #子类二：狗类
    def shout(self):
        print('小狗汪汪汪')
cat=Cat()
cat.shout()
dog=Dog()
dog.shout()

#多态性：一种调用方式，有不同的执行结果
class Animal2(object):
    def eat(self):
        print('我会吃饭')
class Pig(Animal):
    def eat(self):
        print('猪吃猪饲料')
class Dog2(Animal):
    def eat(self):
        print('狗吃狗粮')
#定义一个统一的接口，一个接口多种实现
def test(obj):     #obj形参
    obj.eat()
animal=Animal2()
test(animal)
pig=Pig()
test(pig)
dog2=Dog2()
test(dog2)
#test函数传入不同的对象，执行不同对象的eat方法

#静态方法：@staticmethod，没有self，cls参数的限制
class Person(object):
    @staticmethod
    def study(name):
        print(f'{name}会学习')
    #静态方法既可以使用对象访问，也可以使用类访问
Person.study('xiaoming')
pe=Person()
pe.study('xiaoming')   #调用方法时，传参数

#类方法，使用@classmethod来标识为类方法，一般是以cls作为第一个参数
#类方法内部可以访问类属性，或者调用其他的类方法
class Person3(object):
    name='xiaohong'
    @classmethod
    def sleep(cls):
        print('cls:',cls)
        print('人类在睡觉')
        print(Person3.name)
        print(cls.name)
Person3.sleep()
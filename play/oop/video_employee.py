#单继承
class Person:
    def eat(self):
        print('我会吃饭')
    def sing(self):
        print("我能歌善舞")
class Girl(Person):     #Person类的子类
    pass     #占位符，代码下面不写任何东西，会自动跳过
class Boy(Girl):
    pass
boy=Boy()
boy.eat()
boy.sing()

#方法的重写，重写指的是在子类中定义与父类相同名称的方法
class Person2:
    def money(self):
        print('有一百万要继承')
    def sleep(self):
        print('睡觉了')
class Man(Person2):
    def money(self):      #方法重写了，优先调用自己的
        #Person2.money(self)
        super().money()     #推荐使用第二种
        super().sleep()     #可以调用父类中其他方法
        print('自己赚一千多万')
man=Man()
man.money()
#多继承：子类可以拥有多个父类，并且具有所有父类属性和方法
class Father(object):
    def money(self):
        print('拥有一百万需要被继承')
class Monther(object):
    def appearance(self):
        print('绝世容颜需要被继承')
class Son(Father,Monther):
    pass
s=Son()
s.money()
s.appearance()

#不同的父类有同名的方法，开发时需要尽量避免
class Father2(object):
    def money(self):
        print('拥有一百万需要被继承')
class Monther2(object):
    def money(self):
        print('有一百二十万需要被继承')
class Son2(Monther2,Father2):
    def money(self):
        print('只有十万')
s=Son2()
s.money()

#方法的搜索顺序  __mro__
print(Son2.__mro__)
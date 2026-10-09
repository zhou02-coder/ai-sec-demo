#面向过程和面向对象的区别
#1.面向过程（手洗）：实现一个功能，看重过程，分析一个个步骤。
#用一个个函数实现，再依次调用函数
#2.面向对象（机洗）：实现一个功能，看重谁去帮忙解决这个事情
class Washer:
    height=900
print(Washer.height)
Washer.width=560     #新增类属性:类名.属性名=值
print(Washer.width)
#修改类属性
Washer.height=1200
print('修改后的height:',Washer.height)
#用实例也能访问类属性
wa=Washer()
print('实例也能访问类属性:',wa.height)
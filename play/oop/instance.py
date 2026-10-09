class Washer:
    height=1000
    def wash(self):       #self表示当前调用方法的对象
        print('我会洗衣服')
    def dry(self):
        print('我会烘干衣服')
#实例化对象 对象名=类名
wa=Washer()
#对象调用方法
wa.wash()
wa.dry()
wa2=Washer()
wa2.wash()
wa2.dry()
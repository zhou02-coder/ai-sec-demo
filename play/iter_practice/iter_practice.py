# 可迭代对象Iterable：可以使用for循环遍历的对象
# 遍历（迭代）：依次从对象中把一个个元素取出来的过程
# 数据类型：str、list、tuple、dict、set等
# 可迭代对象的条件：对象必须实现__iter__方法或__getitem__方法；
# __iter__方法返回一个迭代器对象，__getitem__方法根据索引取值
# for循环工作原理：for循环会调用可迭代对象的__iter__方法获取一个迭代器对象，然后不断调用迭代器对象的__next__方法获取下一个元素，直到抛出StopIteration异常为止
# isinstance()函数：判断一个对象是否是某个类的实例，返回True或False
#导入模块
from collections.abc import Iterable, Iterator
# isinstance(obj, Iterable) 判断obj是否是可迭代对象
name="xiaoming"
print(isinstance(name, Iterable))  # True
print(isinstance(name, Iterator))  # False
name2=iter(name)  # 获取迭代器对象
print(isinstance(name2, Iterable))  # True
print(isinstance(name2, Iterator))  # True
# 可迭代对象可以通过iter()转换成迭代器对象，迭代器对象可以通过next()获取下一个元素
# 如果一个对象拥有__iter__方法，那么它就是可迭代对象；
# 如果一个对象拥有__next__方法和__iter__方法，那么它就是迭代器对象
# dir()函数：获取对象的所有属性和方法
#print(isinstance('abc', Iterable))  # True
#print(isinstance([1, 2, 3], Iterable))  # True
#print(isinstance((1, 2, 3), Iterable))  # True
#print(isinstance({'a': 1, 'b': 2}, Iterable))  # True
#print(isinstance({1, 2, 3}, Iterable))  # True

# 迭代器Iterator：可以使用next()函数不断取出下一个元素的对象
#li=[1,2,3,4,5]
#li2=iter(li)  # 获取迭代器对象
#print(next(li2))  
#print(next(li2))  
#print(next(li2))  
# iter()函数：获取可迭代对象的迭代器对象
# next()函数：获取迭代器对象的下一个元素

#自定义迭代器类
class Test(object):
    def __init__(self):
        self.num=0
    def __iter__(self):
        return self  # 返回迭代器对象本身
    def __next__(self):
        if self.num<5:
            num=self.num
            self.num+=1
            return num
        else:
            raise StopIteration  # 抛出异常，表示迭代结束
te=Test()
print(te)
te.__iter__()  # 获取迭代器对象
print(next(te))  # 1
print(next(te))  # 2
print(next(te))  # 3
print(next(te))  # 4
print(next(te))  # 5


# 生成器知识点：
# 列表推导式
li=[i*5 for i in range(5)]
print(li)  # [0, 5, 10, 15, 20]
# 生成器表达式
gen=(i*5 for i in range(5)) # 列表推导式的[]改成了()就成了生成器表达式
print(gen)  
print(next(gen))
print(next(gen))
print(next(gen))
print(next(gen))
print(next(gen))

# 生成器函数：使用yield关键字的函数，每次调用next()函数时，
# 生成器函数会从上一次yield语句处继续执行，直到遇到下一个yield语句或函数结束
# yield关键字：用于定义生成器函数，返回一个生成器对象，
# 类似于return，但不会终止函数的执行，而是暂停函数的执行，保存函数的状态，下次调用next()时从上次暂停的地方继续执行
def test():
    print("start")
    yield 1  # 暂停函数的执行，返回1
    print("continue")
    yield 2  # 暂停函数的执行，返回2
    print("end")
    yield 3  # 暂停函数的执行，返回3
te=test()  # 获取生成器对象
print(te)
print(next(te))  # start 1
print(next(te))  # continue 2
print(next(te))  # end 3

def process_data_stream(data_list):
    for item in data_list:
        processed_item = f'PROCESSED: {item.upper()}'
        yield processed_item
if __name__ == "__main__":
    raw_fruits = ['apple', 'banana', 'cherry']
    fruit_gen=process_data_stream(raw_fruits)
    for fruit in fruit_gen:
        print(fruit)
    manual_gen=process_data_stream(['dog', 'cat', 'fish'])
    print(next(manual_gen))  # PROCESSED: DOG
    print(next(manual_gen))  # PROCESSED: CAT

# 总结：三者关系：可迭代函数，迭代器，生成器
# 可迭代对象Iterable：可以使用for循环遍历的对象
# 迭代器Iterator：可以使用next()函数不断取出下一个元素
# 生成器Generator：使用yield关键字的函数，每次调用next()函数时，
# 生成器函数会从上一次yield语句处继续执行，直到遇到下一个yield语句或函数结束
# 迭代器不一定是生成器，生成器一定是迭代器
# 包含关系：可迭代对象Iterable包含迭代器Iterator，迭代器Iterator包含生成器Generator

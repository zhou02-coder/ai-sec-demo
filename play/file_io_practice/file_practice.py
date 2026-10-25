#文件就是存储在某种长期存储设备上的一段数据
#文件操作：打开--->读、写文件--->关闭文件
a=open('d:/ai-sec-demo/play/file_io_practice/test.txt')
print(a.name)  #文件名
print(a.mode)
print(a)
#print(a.read(6))  #最多读取6个数据
#print(a.readline())
#print(a.readline())
#te=a.readlines()   #返回列表
#print(te)
#print(type(te))    #<class 'list'>      
#while True:
   # text=a.readline()  #读取一行内容  
    #读取完内容了，要退出循环
    #if not text:
        #break
    #print(text)
#a.close()

#访问模式
#file=open('d:/ai-sec-demo/play/file_io_practice/test01.txt','w+')   #重新编辑文件内容，原有内容就会被覆盖
#print(file.read())
#file.write('xiaomingxiaohong666')
#file.close()
file=open('d:/ai-sec-demo/play/file_io_practice/test01.txt','a+')
print(file.read())
file.write('jack haha')
file.close()

#文件定位操作：tell()和seek()
#tell()：显示文件内当前位置，即文件指针当前位置
#seek(offset，whence)：移动文件读取指针到指定位置
#offset：偏移量，表示要移动的字节数
#whence：起始位置，表示移动字节的参考位置，默认是0，0代表文件开头；1代表当前位置；2代表文件结尾
#seek(0,0)就会把文件指针移到文件开头
a=open('d:/ai-sec-demo/play/file_io_practice/test.txt','w+')
a.write('hello,python!')
pos=a.tell()     #13---文件内容长度
print('当前文件指针所在的位置:',pos)
a.seek(0)
pos2=a.tell()
print('移动后所在位置:',pos2)
print(a.read())
a.close()

#编码格式
#with open：代码执行完，系统会自动调用f.close(),可以省略文件关闭步骤
with open('d:/ai-sec-demo/play/file_io_practice/test02.txt','w+',encoding='utf-8') as b:
    b.write('小明18岁了\n好厉害')
    b.seek(0)
    print(b.read())

import os
#os.rename('d:/ai-sec-demo/play/file_io_practice/test01.txt','xiaoming.txt')  #文件重命名
#os.remove('D:/ai-sec-demo/xiaoming.txt')    #删除文件
#os.mkdir('bingibing')                       #创建文件夹
#os.rmdir(r'D:\ai-sec-demo\bingibing')       #删除文件夹
#print(os.getcwd())                          #获取当前目录
#print(os.listdir())                         #获取目录列表


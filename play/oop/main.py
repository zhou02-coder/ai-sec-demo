from employee import Employee,GeneralStaff,HRAdmin
print('-'*30)
print('【测试1:基础员工】')
emp=Employee('Jack','E001')
emp.set_salary(6600)
emp.show_info()
print('-'*30)
print('【测试2:普通正式员工(单继承)】')
staff=GeneralStaff('Anna','E002','研发部')
staff.set_salary(9000)
staff.show_info()
print('-'*30)
print('【测试3:HR管理员(继承传递+方法重写)】')
hr=HRAdmin('Bern','H001','人事部','高级')
hr.set_salary(13000)
hr.show_info()
print('='*30)
print('【安全测试:非法薪资输入】')
test_emp=Employee('测试账号:','T001')
test_emp.set_salary(-3000)  #负数
test_emp.set_salary('8000')  #字符串
test_emp.show_info()
print('='*30)
print('【边界安全测试:尝试直接读取私有薪资】')
test_emp=Employee('xiaoming','E005')
test_emp.set_salary(7500)   #测试：直接访问__salary会之际报错
try:
    print(test_emp.__salary)
except AttributeError as e:
    print(f'X 尝试访问.__salary,报错:{e}')
    #绕过防护写法
print(f'! 绕过防护写法,test_emp._Employee__salary={test_emp._Employee__salary}')
    #普通员工强行读取
print('-'*20)
staff_test=GeneralStaff('Anna','E006','研发部')
staff_test.set_salary(8800)
print(f'普通员工强行读取:staff_test._Employee__salary={staff_test._Employee__salary}')
print('重点:代码语法上面能读到!这就说明:python私有属性不是强加密')
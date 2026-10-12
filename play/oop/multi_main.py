from employee import Employee
class SalaryViewMixin:    
    def view_salary(self):     #view_salary查看薪资
        print('权限验证通过,允许查看薪资')
        print(f'管理员可查看薪资:{self._Employee__salary}')
        #同名方法，用来测试MRO优先级
    def show_info(self):
        print('这是SalaryViewMixin里面的show_info')
#多继承：AdminStaff同时继承Employee和SalaryViewMixin
#括号顺序=MRO查找优先级，左边优先
class AdminStaff(Employee,SalaryViewMixin):
    pass
if __name__=='__main__':   #创建管理员实例
    admin=AdminStaff(name='田中',job_id='A001')
    admin.set_salary(75000)
    print('===1.多继承功能测试===')
    admin.show_info()
    print()
    admin.view_salary()
    print('===2.MRO同名方法优先级测试===')
    print('调用show_info,优先执行写在左边的父类方法')
    admin.show_info()
    print('===3.打印MRO查找顺序===')
    print('方法查找顺序')
    for item in AdminStaff.__mro__:
        print(f'-{item}')
    print('===4.安全边界测试:多继承能不能突破私有属性?===')
    try:
        print(admin.__salary)
    except AttributeError as err:
        print(f'X 访问报错:{err}')
        print('结论:就算使用多继承,依然无法直接访问私有属性,封装保护失效')


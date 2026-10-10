class Employee:
    #类属性:公司名称，全体员工共享
    company='xx科技有限公司'
    #构造函数:初始化员工信息,创建对象时自动触发
    def __init__(self,name,position,base_salary):
        #公开实例属性：姓名，岗位，外部可直接查看
        self.name=name
        self.position=position
        #私有属性：基础薪资，封装核心，外部无法直接访问修改
        self.__base_salary=base_salary
        print(f'{self.name}记录已经创建')
    
    #析构函数：对象被销毁时自动执行
    #业务用途：员工记录销毁时留下操作日志，符合企业数据操作留痕规范
    def __del__(self):
        print(f'[日志]员工{self.name}的记录对象已经销毁')
   
    #私有方法：薪资调整幅度检验，仅类内部可以调用
    def __check_salary_valid(self,new_salary):
    #公司规则：单次薪资调整幅度不得超过原薪资的50%
        max_allowed=self.__base_salary*1.5
        if 0<new_salary<=max_allowed:
            return True
        return False
    
    #公共方法：打印员工公开信息（不泄露敏感薪资）
    def show_public_info(self):
        print(f'员工姓名:{self.name}')
        print(f'岗位:{self.position}')
        print(f'所属公司:{self.company}')
        print('-'*30)
    #公共方法：HR专属查询薪资窗口
    def get_salary(self):
        print(f'{self.name}当前薪资:{self.__base_salary}元')
    #公共方法：调整薪资，必须经过内部规则检验
    def adjust_salary(self,new_salary):
        if self.__check_salary_valid(new_salary):
            self.__base_salary=new_salary
            print(f'{self.name}的薪资调整成功,最新薪资:{self.__base_salary}元')
        else:
            print('调整失败:单次薪资涨幅不得超过50%,且薪资必须大于0')

    #创建员工实例，触发构造函数
emp1=Employee('李明','后端开发工程师',10000)
print('1.查看公开信息')
emp1.show_public_info()
print('2.HR查询薪资')
emp1.get_salary()
print('3.违规调薪测试(涨幅100%)')
emp1.adjust_salary(20000)
print('4.合规调薪测试(涨幅40%)')
emp1.adjust_salary(14000)
emp1.get_salary()
print('5.销毁员工记录,触发析构函数')
del emp1
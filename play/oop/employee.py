class Employee:     #父类，最基础的员工
    def __init__(self,name,job_id):
        self.name=name     #公开信息
        self.job_id=job_id
        self.__salary=0    #敏感数据，私有封装
    def set_salary(self,amount):  #设置薪资：内置安全校验
        #安全点：必须是正数，数字类型
        if isinstance(amount,(int,float))and amount>0:
            self.__salary=amount
        else:
            print('安全拦截:薪资输入非法,必须为正数字')
    def show_info(self):   #父类原始方法：只展示公开信息
        print(f'姓名:{self.name}')
        print(f'工号:{self.job_id}')
        print('薪资:【无权限查看】')
class GeneralStaff(Employee):   #子类，单继承Employee
    def __init__(self, name, job_id,department):
        #super()调用父类构造方法
        super().__init__(name,job_id)
        self.departmnt=department
    def show_info(self):
        #方法重写+super()扩展：先执行父类逻辑，再加本层内容
        super().show_info()
        print(f'部门:{self.departmnt}')
class HRAdmin(GeneralStaff):  #孙子类：HR管理员，演示继承传递
    def __init__(self, name, job_id, department,level):
        super().__init__(name,job_id,department)
        self.level=level  #管理员等级
    def show_info(self):  #重写方法：super()执行上级展示逻辑
        super().show_info()  #扩展权限：HR可查看敏感薪资数据
        print(f'管理员等级:{self.level}')
        print(f'薪资:{self._Employee__salary}元')
        
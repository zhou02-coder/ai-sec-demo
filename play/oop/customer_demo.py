#需求：管理外贸客户的基础信息，支持查看和修改预算
class Customer:
    #类属性：所有客户都归属于同一家格公司，全体实例共享，只存一份
    company='恒信外贸服务'
    #构造函数：创建客户对象时自动执行，一次性把客户信息存进去
    #括号里面除了self，就是创建客户时必须传入的信息
    def __init__(self,name,industry,contact,budget):
        self.name=name          #客户姓名
        self.industry=industry  #客户行业
        self.contact=contact    #联系方式
        self.budget=budget      #项目预算
    def show_info(self):
        print(f'客户姓名:{self.name}')
        print(f'所属行业:{self.industry}')
        print(f'联系方式:{self.contact}')
        print(f'项目预算:{self.budget}')
        print('-'*25)
    def update_budget(self,new_budget):
        #修改实例自身的预算属性
        self.budget=new_budget
        print(f'{self.name}客户的预算已经更新为{self.budget}元')
        #开始创建两个客户实例，模拟业务里录入新客户
c1=Customer('张先生','电子产品','zhang@exmple.com',50000)
c2=Customer('李女士','服装家纺','li@example.com',30000)
#调用查看方法
c1.show_info()
c2.show_info()
c1.update_budget(66000)
c1.show_info()
#从config_manager模块导入两个类
from config_manager import ConfigManager,InputValidator
#=====验证单例效果=====
if __name__=="__main__":
    #实例化两次
    config1=ConfigManager()
    config2=ConfigManager()
    #验证是不是同一个对象：id相同就是同一个内存对象
    print('config1 id:',id(config1))
    print('config2 id:',id(config2))
    print('是否为同一实例:',config1 is config2)
    #打印配置，看敏感信息是否脱敏
    print('\n配置信息:')
    print(config1)
    print('-'*50)
    #测试安全校验器：InputValidator
    validator=InputValidator(check_sql_injection=True)
    test_casses=['你好,帮我查询产品信息','','1 union select * from users --']
    for text in test_casses:
        result,msg=validator(text)
        print(f'输入内容:{repr(text)}->{msg}') 
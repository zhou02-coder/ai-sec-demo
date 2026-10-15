#ConfigManager:单例全局配置管理器
import re
class ConfigManager:
    #类变量：保存唯一的实例引用，初始为空
    _instance=None
    #标记：是否已经执行过初始化，避免重复加载配置
    _initialized=False
    #魔法方法：__new__:真正创建对象的方法，在__init__之前执行
    def __new__(cls,*args,**kwargs):
        #判断：如果还没有实例，就创建一个
        if cls._instance is None:    #调用父类object的__new__，创建真正的对象
            cls._instance=super().__new__(cls)
            #不管调用多少次，永远返回同一个实例
        return cls._instance
    #魔法方法：__init__:实现初始化，给对象赋值
    def __init__(self):
        #只初始化一次，第二次实例化跳过
        if ConfigManager._initialized:
            return
        #模拟加载项目配置（真实项目里从配置文件/环境变量读取）
        self.db_host='127.0.0.1'
        self.db_port=3306
        #敏感配置：API密钥、数据库密码
        self.openai_api_key='sk-abc123def456ghi789jkl012'
        self.db_password='my_db_password_123'
        self.security_enable=True   #安全功能总开关
        #标记为已经初始化
        ConfigManager._initialized=True
    #魔法方法：__str__:打印对象时的友好输出
    def __str__(self):
        #使敏感信息脱敏：密钥只显示前三位+后三位，中间用'*'代替
        mask_key=self.openai_api_key[:3]+'*'*10+self.openai_api_key[-3:]
        mask_pwd='*'*12
        #返回格式化的配置信息，不泄露完整敏感值
        return (f'[ConfigManager] 数据库:{self.db_host}:{self.db_port}\n' f'API密钥:{mask_key}\n' f'数据库密码:{mask_pwd}\n' f'安全开关:{self.security_enable}')
#安全输入校验类，用到__call__魔法方法
class InputValidator:
    def __init__(self,check_sql_injection=True):
        #check_sql_injection:是否开启SQL注入检测
        self.check_sql_injection=check_sql_injection
        #正则匹配SQL高危关键词，IGNORECASE忽略大小写
        self.sql_pattern=re.compile(r'(union|select|insert|delete|drop|update|alter|exec|script)',re.IGNORECASE)
        #魔法方法__call__魔法方法：让实例可以像函数一样()调用
    def __call__(self, input_str):
        #input_str：用户输入的字符串
        if not input_str or not input_str.strip():
            return False, '输出不能为空'
        if self.check_sql_injection:
            if self.sql_pattern.search(input_str):
                return False, '输入包含非法内容,存在安全风险'
            return True, '校验通过'       
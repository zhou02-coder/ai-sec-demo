class BaseTask:    #基础任务父类：定义所有任务统一接口，实现多态约束
    def __init__(self,task_id:str,task_name:str):
        #task_id:任务唯一编号
        #task_name:任务显示名称
        self.task_id=task_id
        self.task_name=task_name
    def run(self):   #统一执行入口，子类必须重写此方法（多态核心）
        raise NotImplementedError('所有任务子类必须实现run()方法')
    @classmethod
    def create_task(cls,task_type:str,task_id:str):   #类方法：任务工厂
        #根据传入的任务类型，自动创建对应的任务实例；调用方无需关心每个子类的具体实现，只需要传类型和ID
        #先校检任务格式
        if not cls.check_task_id(task_id):
            raise ValueError(f'任务ID格式非法:{task_id}')
        if task_type=='export':
            return ExportTask(task_id)
        elif task_type=='log_clear':
            return LogClearTask(task_id)
        elif task_type=='db_backup':
            return DbBackupTask(task_id)
        else:
            raise ValueError(f'不支持的任务类型:{task_type}')
    @staticmethod
    def check_task_id(task_id:str) ->bool:
        #静态方法：任务ID格式检验；纯工具函数，不需要访问类属性，实例属性，也不需要创建对象
        #只负责输入格式检验，返回布尔结果
        #校检规则：非空字符串，长度不小于3
        return isinstance(task_id,str) and len(task_id)>=3
class ExportTask(BaseTask):    #csv数据导出任务子类
    def __init__(self, task_id:str):
        super().__init__(task_id,'csv数据导出')
    def run(self):
        #重写父类run方法，实现导出业务逻辑
        print(f'[执行]{self.task_name}|任务ID:{self.task_id}')
        print('->正在读取业务数据表...')
        print('->正在生成csv文件...')
        print('数据导出完成,文件已保存')
        print()
class LogClearTask(BaseTask):   #过期日志清理任务子类
    def __init__(self, task_id:str):
        super().__init__(task_id,"过期日志清理")
    def run(self):
        #重写父类run方法，实现日志清理逻辑
        print(f'[执行]{self.task_name}|任务ID格式:{self.task_id}')
        print('->s扫描7天前的日志文件...')
        print('->正在删除过期日志...')
        print('日志清理完成,释放磁盘空间')
        print()
class DbBackupTask(BaseTask):   #数据库备份任务子类
    def __init__(self, task_id:str):
        super().__init__(task_id,"数据库备份")
    def run(self):
        #重写父类run方法，实现备份逻辑
        print(f'[执行]{self.task_name}|任务ID格式:{self.task_id}')
        print('->正在锁定数据库表...')
        print('->正在全量导出备份文件...')
        print('数据库备份完成,已上传存储')
if __name__=='__main__':
    #1.演示静态方法：直接通过类调用，无需创建对象
    print('===静态方法测试===')
    print('合法ID校检结果:',BaseTask.check_task_id('exp001'))
    print('非法ID校检结果:',BaseTask.check_task_id('ab'))
    print()
    #2.演示类方法：通过工厂批量创建不同类型的任务
    print('===创建任务列表===')
    task_list=[BaseTask.create_task('export','exp001'),BaseTask.create_task('log_clear','log002'),BaseTask.create_task('db_backup','bak003')]
    #3.演示多态：统一调用run()，自动匹配对应子类的实现
    print('===任务调度执行(多态核心)===')
    for task in task_list:
        task.run()
        #调度器不需要知道当前task具体是什么类型
        #只需要统一调用run()，各自执行自己的逻辑
                
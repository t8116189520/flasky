# coding:utf8

from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

# 从app目录中导入工厂函数，用于创建app
from app import create_app,db
from app.models import User,Role,Permission

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app,db)
# 添加db命令，用于数据库迁移
manager.add_command('db',MigrateCommand)

def make_shell_context():
    # 返回上下文
    return dict(app=app,db=db,User=User,Role=Role,Permission=Permission)
# 添加命令行操作数据库功能
manager.add_command('shell',Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run() # 使用manager.run()

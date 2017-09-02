# coding:utf8

import os
# 获取当前文件所在目录的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))

# 配置的基类
class Config:
    '''设置密钥，确保不被跨站请求伪造攻击'''
    SECRET_KEY = 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass
    # 虽然什么都没做，但仍然定义，好处在于衍生类当中可以继承并重写

class DevelopmentConfig(Config):
    Debug = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir,'data-dev.sqlite')

class TestingConfig(Config):
    Testing = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

'''
定义一个基类，三个衍生类的好处：
相同的配置放在基类里；
不同的配置放在衍生类里。
'''

config = {
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,

    'default':DevelopmentConfig
}

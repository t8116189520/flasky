# coding:utf8

from datetime import datetime

from . import db
from . import login_manager

# 密码散列值
from werkzeug.security import generate_password_hash,check_password_hash

# 生成和检验邮件确认令牌
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# 要使用SECRET_KEY，就要用到当前app，也就是current_app
from flask import current_app

# UserMixin类包含一些用户方法的默认实现，直接继承即可
from flask_login import UserMixin

class Permission:
    FOLLOW = 0x01 # 关注其他用户的权限为0b00000001
    COMMET = 0x02 # 发表评论的权限为0b00000010
    WRITE_ARTICLES = 0x04 # 写文章的权限为0b00000100
    MODERATE_COMMETS = 0x08 # 审查评论的权限为0b00001000
    ADMINISTER = 0x80 # 管理员权限为0b10000000

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User',backref='role')
    default = db.Column(db.Boolean,default=False) # 只有普通用户为True，其他角色为False
    permissions = db.Column(db.Integer) # 角色具有哪些权限

    @staticmethod #静态方法：能够直接用类名调用该方法
    def insert_roles(): # 插入角色种类，默认有3个角色：普通用户，协管员，管理员
        roles = {
            # User具有前三个权限
            # User里的True，代表是默认的角色
            'User':(Permission.FOLLOW|Permission.COMMET|Permission.WRITE_ARTICLES,True),
            'Moderator':(Permission.FOLLOW|
                         Permission.COMMET|
                         Permission.WRITE_ARTICLES|
                         Permission.MODERATE_COMMETS,False),
            'Administer':(0xff,False)# False代表不是默认角色，因为不能让每一个用户都变成管理员

        }
        for r in roles:
            # 先查找是否已存在该角色
            role = Role.query.filter_by(name=r).first()
            if role is None: # 如果不存在该角色，就创建该角色
                role = Role(name=r)
            role.permissions = roles[r][0] # 把权限赋予该角色
            role.default = roles[r][1] # 是否为默认角色
            db.session.add(role)
        db.session.commit()



    def __repr__(self):
        return '<Role %r>'%self.name

class User(UserMixin,db.Model):
    __tablename__ = 'users'

    def __init__(self,**kwargs): # 初始化函数，用于在用户注册时赋予角色
        super(User,self).__init__(**kwargs) # 先执行基类的初始化函数
        if self.email == 'nanfengpo':  # 如果用户注册时填写的邮箱是'nanfengpo'，那么该用户就被设置为管理员
            # self.role是在Role模型中通过db.relationship定义的一个反向引用，可以直接当做属性来使用
            self.role = Role.query.filter_by(permissions=0xff).first() # 0xff表示所有权限都有
        else:
            self.role = Role.query.filter_by(default=True).first()

    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    email = db.Column(db.String(64),unique=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    name = db.Column(db.String(32))
    location = db.Column(db.String(128))
    about_me = db.Column(db.Text()) # 个人简介
    member_since = db.Column(db.DateTime(),default = datetime.utcnow) # 用户注册的时间
    last_seen = db.Column(db.DateTime(),default = datetime.utcnow) # 上一次登录的时间


    # 设置密码列，用于保存密码的散列值
    password_hash = db.Column(db.String(128))

    # 用户状态列，当邮件令牌通过时，为True；否则为False
    confirmed = db.Column(db.Boolean,default=False)

    # 使用property装饰器，把密码变成私有财产，不允许访问
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # 使用password.setter装饰器，允许写入密码
    @password.setter
    def password(self,pw):
        self.password_hash=generate_password_hash(pw) # 输入是原密码，输出是加密后的密码散列值

    # 验证用户填写的密码是否正确
    def verify_password(self,pw):
        return check_password_hash(self.password_hash,pw) # 输入是用户填写的密码已经本地存储的密码散列值，输出是验证结果

    # 生成邮件确认令牌
    def generate_confirmation_token(self,expiration=3600):
        # current_app的用法和我们之前的app的用法一致
        s = Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)
        return s.dumps({'confirm':self.id})

    # 验证邮件确认令牌
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY']) # 这里不需要加上有效期
        try:
            data = s.loads(token)
        except: # 如果不能由token得到值，说明token是假的令牌
            return False
        if data.get('confirm') != self.id:  # 如果由token得到的值不正确，也是假的令牌
            return False
        self.confirmed = True # 激活账户
        db.session.add(self) # 在数据库当中修改用户信息，在这里，只修改了self.confirmed
        return True

    # 生成重设密码确认令牌
    def generate_reset_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)
        return s.dumps({'reset':self.id}) # 使用reset作为字典的key，表示当前令牌的作用

    # 根据token来重设密码
    def reset_password(self,token,new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False # 如果不能由token解码，则返回错误
        if data.get('reset') != self.id:
            return False # 如果由token解码得到的id不符合，也返回错误
        self.password = new_password  # 如果前面没有返回False，表示令牌是正确的。因此修改密码
        db.session.add(self)
        return True

    # 判断用户是否具有某种权限
    def can(self,permissions):
        return self.role is not None and (self.role.permissions & permissions)==permissions

    # 判断用户是否为管理员
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    # 每次登录都要刷新最后登录时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)


    def __repr__(self):
        return '<User %r>'%self.username

# Flask-login要求实现一个回调函数，通过user_id 加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 定义一个匿名用户类
from flask_login import AnonymousUserMixin
class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

    def is_administrator(self):
        return False

# 让登录管理器识别匿名用户类
login_manager.anonymous_user = AnonymousUser
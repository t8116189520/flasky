
# coding:utf8

from functools import wraps # wraps是包裹的意思
from flask import abort # abort用于报错
from flask_login import current_user # 导入当前用户

from models import Permission

# 自定义装饰器，根据当前用户是否具有permission权限来判断是否执行函数f
def permission_required(permission):
    def decorator(f): # f是function的简称
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not current_user.can(permission):
                abort(403) # 如果不具有权限，则不执行f，返回一个403错误，禁止访问
            return f(*args,**kwargs) # 如果具有权限，我们就执行f
        return decorated_function # 返回自己
    return decorator # 返回自己

# 只有管理员才能执行f
def admin_required(f):
    return permission_required(Permission.ADMINISTER)
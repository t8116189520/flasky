# coding:utf8
# 导入蓝本包
from flask import Blueprint
# 创建一个蓝本，取名为main
# 相当于app=Flask(__name__)
main = Blueprint('main',__name__)

# . 代表当前目录，也就是main这个目录
from . import errors,views


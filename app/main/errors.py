# coding:utf8

# 这里的main不是目录！而是__init__.py里面的main蓝本
# 只有__init__.py里的东西可以直接导入
from . import main

from flask import render_template

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

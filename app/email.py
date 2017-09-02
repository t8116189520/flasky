# coding:utf8

from flask_mail import Message
from . import mail
from flask import render_template,current_app

from threading import Thread

def send_async_email(app,msg):
    # 必须在程序上下文当中使用mail
    with app.app_context():
        mail.send(msg)

def send_email(to,subject,template,**kwargs):
    # 通过current_app获取当前的程序实例app
    app = current_app._get_current_object()
    msg = Message(subject=subject,
                  sender='abc',
                  recipients=[to])
    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr
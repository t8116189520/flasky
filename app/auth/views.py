# coding:utf8

from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,logout_user,login_required
from flask_login import current_user # 当前用户
from . import auth
from .forms import LoginForm,RegisterForm,ChangePasswordForm,PasswordResetRequestForm,PasswordResetForm
from ..models import User,Permission
from ..email import send_email
from .. import db # 实际上是 from ..__init__ import db
from ..decorators import admin_required,permission_required

@auth.route('/login/',methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # 在数据库中查找该邮箱的用户
        user = User.query.filter_by(email=form.email.data).first()
        # 如果数据库中存在该用户，且表单中填写的密码验证通过
        if user is not None and user.verify_password(form.password.data):
            # 使用login_user来登录用户
            login_user(user,form.remember.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid email or password')
    return render_template('auth/login.html',form=form)

@auth.route('/logout/')
@login_required # 表示必须在已经登录的情况下才能访问这个路由
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))

# 注册路由
@auth.route('/register/',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit() # 要求立即更改数据库，用于发送确认令牌，手动添加db.session.commit()
        token = user.generate_confirmation_token(expiration=1800) # 得到确认令牌
        # 发送邮件
        send_email(user.email,'Confirm your account','auth/mail/confirm',user=user,token=token)
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)

# 确认令牌路由，用于点击邮件的确认链接
@auth.route('/confirm/<token>') # 这里的token是注册路由中得到的，并通过邮件发送给用户，由用户来点击本路由
@login_required # 要求在已登录的状态下激活
def confirm(token):
    if current_user.confirmed:  # 多次点击确认令牌时，confirmed已经为True，此时直接跳转到主界面
        return redirect(url_for('main.index'))
    if current_user.confirm(token): # 第一次点击确认令牌时，会激活账户
        flash('You have confirmed you account!')
    else:   # 确认令牌的时间过期了
        flash('Invalid token')
    return redirect(url_for('main.index'))

@auth.route('/change-password/',methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # 首先看旧密码是否输入正确
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            # 这里的add是修改现有用户
            db.session.add(current_user)
            flash('your password has been updated')
            return redirect(url_for('main.index'))
        else:
            # 如果旧密码输错，则提示信息
            flash('invalid password')
    return render_template('auth/change_password.html',form=form)

# /reset/后面没有跟变量的，这个路由只实现请求重设密码
@auth.route('/reset/',methods=['GET','POST'])
def password_reset_request():
    if not current_user.is_anonymous: #如果该用户不是匿名的，也就是已登录，则直接跳转到主页面
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email,'Reset password',
                       'auth/mail/reset_password',user=user,token=token)
        flash('An email has been sent to you')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)

# /reset/后面有token变量，这个路由实现重设密码
@auth.route('/reset/<token>',methods=['GET','POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.reset_password(token,form.password.data):
            flash('your password has been updated')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    # 两个视图函数都是渲染auth/reset_password.html，不同之处在于form不一样
    return render_template('auth/reset_password.html',form=form)

# 用户每次登录之前，都ping一下，刷新最后一次访问时间
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()

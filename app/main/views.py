# coding:utf8

from . import main
from flask import render_template,session,redirect,url_for,current_app,flash

from ..decorators import admin_required,permission_required
from ..models import Permission
from flask_login import login_required,current_user
from .forms import EditProfile

from .. import db
from .. import bootstrap

# 导入模型/表单/邮件
from ..models import User
from .forms import NameForm
from ..email import send_email

@main.route('/',methods=['GET','POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        # 在数据库中查找该用户是否存在
        user = User.query.filter_by(username=form.name.data).first()
        # 如果是新用户
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            send_email('nanfengpo','New user','mail/new_user',user=user)
        else: # 如果是已存在的用户
            session['known'] = True
        session['name'] = form.name.data
        # post/重定向/get模式
        return redirect(url_for('main.index'))
    return render_template('index.html',
                           form = form,
                           name = session.get('name'),
                           known = session.get('known'))

@main.route('/admin/')
@login_required
@admin_required
def admin_only():
    return 'you are admin'

@main.route('/moderator/')
@login_required
@permission_required(Permission.MODERATE_COMMETS)
def moderator():
    return 'you are moderator'

# 显示用户资料
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html',user=user)

# 编辑用户资料：使用表单
@main.route('/edit-profile/',methods = ['GET','POST'])
@login_required
def edit_profile():
    form = EditProfile()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('your profile has been updated')
        return redirect(url_for('main.user',username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form)
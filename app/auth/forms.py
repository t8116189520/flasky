
# coding:utf8
from flask_wtf import FlaskForm
# 导入表单的各个字段
from wtforms import StringField,SubmitField,BooleanField,PasswordField
# 从wtforms当中导入验证异常，用于提示字段验证错误
from wtforms import ValidationError
# 导入验证函数。Email表示输入的必须是电子邮件，Length限制输入的长度
from wtforms.validators import DataRequired,Email,Length,EqualTo

from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(),Length(1,64)])
    password = PasswordField('Password:',validators=[DataRequired(),Length(6,20)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log In')

# 注册页面的表单类
class RegisterForm(FlaskForm):
    # 设置email字段
    email = StringField('Email: ',validators=[DataRequired(),Length(1,64)])
    # username字段
    username = StringField('Username: ',validators=[DataRequired(),Length(1,64)])
    # password字段
    password = PasswordField('Password: ',validators=[DataRequired(),Length(6,20)])
    # 确认密码字段
    # EqualTo有两个参数，分别是和哪一个字段相等，以及输错时的提示信息
    password2 = PasswordField('Confirm your pasword: ',
                              validators=[DataRequired(),
                                          EqualTo('password',message='passwords must match')])
    submit = SubmitField('Register')

    # 函数名要求必须以validate_开头，字段名结尾
    # 自动被调用，不需要使用这些函数
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')

# 修改密码的表单
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password',validators=[DataRequired()])
    password = PasswordField('New password',validators=[DataRequired(),Length(6,20)])
    password2 = PasswordField('Confirm new password',
                              validators=[DataRequired(),
                                          EqualTo('password',message='passwords must match')])
    submit = SubmitField('Update Password')

# 请求重设密码的表单
class PasswordResetRequestForm(FlaskForm):
    # email字段：告诉系统需要重设哪一个账户的密码
    email = StringField('Email',validators=[DataRequired(),Length(1,64)])
    submit = SubmitField('Reset Password')

    # 邮箱的验证条件：必须在数据库中存在该用户
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address')

class PasswordResetForm(FlaskForm):
    email = StringField('Email',validators=(DataRequired(),Length(1,64)))
    password = PasswordField('New Password',validators=[DataRequired(),Length(6,20)])
    password2 = PasswordField('Confirm Password',
                              validators=[DataRequired(),
                                          EqualTo('password',message='passwords must match')])
    submit = SubmitField('Reset Password')

    # 邮箱的验证条件：必须在数据库中存在该用户
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address')
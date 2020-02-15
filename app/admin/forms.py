from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, length, EqualTo
from wtforms import StringField, PasswordField, SubmitField


# 管理员登陆表单
class adminForm(FlaskForm):
    account = StringField(label="请输入账号", validators=[DataRequired("账号不能为空!")],
                          render_kw={"class": "admin-account",
                                     "placeholder": "请输入账号",
                                     "required": "required"})
    password = PasswordField(label="请输入密码", validators=[DataRequired("密码不能为空!")],
                             render_kw={"class": "admin-pwd",
                                        "placeholder": "请输入密码",
                                        "required": "required"})
    submit = SubmitField(label="登录", render_kw={"class": "admin-submit"})


from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, length, EqualTo
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from flask_wtf.file import FileAllowed, FileField

TAG_LIST = ["动画", "番剧", "音乐", "舞蹈", "游戏", "科技", "生活", "鬼畜", "时尚", "娱乐", "影视"]


class RegistForm(FlaskForm):
    name = StringField(label="请输入用户名", validators=[DataRequired("用户名不能为空!")],
                       render_kw={"class": "regn"})
    password1 = PasswordField(label="请输入密码", validators=[DataRequired("密码不能为空!")],
                              render_kw={"class": "regp1"})
    password2 = PasswordField(label="确认密码", validators=[EqualTo("password1", "两次密码不一致!")],
                              render_kw={"class": "regp2"})
    email = StringField(label="请输入邮箱", validators=[DataRequired("邮箱不能为空")],
                        render_kw={"class": "rege"})
    submit = SubmitField(label="注册", render_kw={"class": "regsub"})


class LoginForm(FlaskForm):
    name = StringField(label="请输入用户名", validators=[DataRequired("用户名不能为空!")],
                       render_kw={"class": "logn"})
    password = PasswordField(label="请输入密码", validators=[DataRequired("密码不能为空!")],
                             render_kw={"class": "logp"})
    submit = SubmitField(label="登录", render_kw={"class": "logsub"})


class Userinfo(FlaskForm):
    info = TextAreaField(label="个人简介", validators=[DataRequired("用户名不能为空")], render_kw={"class": "info-info"})

    face = FileField(label="请上传头像", validators=[FileAllowed(["jpg", "png"])],
                     render_kw={"class": "info-face",
                                "enctype": "multipart/form-data"})

    submit = SubmitField(label="提交", render_kw={"class": "info-submit"})


class PwdForm(FlaskForm):
    password1 = PasswordField(label="请输入新密码", validators=[DataRequired("密码不能为空!")],
                              render_kw={"class": "pwd1"})
    password2 = PasswordField(label="确认密码",
                              validators=[DataRequired("密码不能为空"), EqualTo("password1", "两次密码不一致!")],
                              render_kw={"class": "pwd2"}
                              )
    submit = SubmitField(label="确认", render_kw={"class": "pwd-submit"})


class CommentForm(FlaskForm):
    comment = TextAreaField(label="请输入评论", validators=[DataRequired("评论不能为空")],
                            render_kw={"class": "comment-area",
                                       "placeholder": "在这里输入你的评论"})
    submit = SubmitField(label="发表", render_kw={"class": "comment-submit"})


class CreateForm(FlaskForm):
    video_title = StringField(label="视频标题", validators=[DataRequired("标题不能为空")],
                              render_kw={"class": "create-title"})
    info = TextAreaField(label="视频简介",
                         render_kw={"class": "create-info"})
    face = FileField(label="视频封面", validators=[FileAllowed(["jpg"])], render_kw={"class": "create-face"})
    tags = [(t, t) for t in TAG_LIST]
    tag = SelectField(label="分类", choices=tags, render_kw={"class": "create-radio"})

    video_file = FileField(label="视频文件", validators=[FileAllowed(["mp4"])], render_kw={"class": "create-video"})

    submit = SubmitField(label="提交", render_kw={"class": "create-submit"})

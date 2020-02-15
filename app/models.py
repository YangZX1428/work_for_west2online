from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

"""
    该程序用于创建数据库模型类
    并创建相应的表
"""
app = Flask(__name__)


class Config():
    SECRET_KEY = "asdasda"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:4343594.@127.0.0.1:3306/myweb"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


app.config.from_object(Config)
db = SQLAlchemy(app)


# 配置参数


# 用户
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)  # 用户id
    name = db.Column(db.String(100), unique=True)  # 用户名
    password = db.Column(db.String(20))  # 密码
    email = db.Column(db.String(30), unique=True)  # 邮箱
    info = db.Column(db.Text, default="None")  # 简介
    face = db.Column(db.String(100), default="None")  # 头像
    userlogs = db.relationship('Userlog', backref="user")  # Userlog与user表绑定,关联
    comment = db.relationship('Comment', backref="user")  # 与评论类关联
    favorite = db.relationship('Favorite', backref="user")  # 与收藏类关联

    def __repr__(self):
        return "<User:" + self.name + ">"


# 登录日志,一个用户可对应多个登录日志
class Userlog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # 所属用户(通过外键与user表相关联)
    time = db.Column(db.DateTime, index=True, default=datetime.now())  # 登陆时间，默认为当前时间


# 标签
class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)  # 标签id
    tag_name = db.Column(db.String(100), unique=True)  # 标签名
    videoes = db.relationship("Video", backref="tag")  # 该标签关联视频


# 视频
class Video(db.Model):
    __tablename__ = "video"
    id = db.Column(db.Integer, primary_key=True)  # 视频id
    video_title = db.Column(db.String(100), unique=True)  # 视频标题
    url = db.Column(db.String(255), unique=True)  # 视频url
    info = db.Column(db.Text, default="该视频无简介!")  # 视频简介
    face = db.Column(db.String(255), default="None")  # 视频封面
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))  # 视频所属tag
    Goodnum = db.Column(db.Integer, default=0)  # 视频点赞数
    danmaku = db.Column(db.Integer, default=0)  # 视频弹幕数
    comment = db.relationship('Comment', backref="video")  # 视频评论外键关联
    favorite = db.relationship('Favorite', backref="video")  # 视频收藏外键关联


# 评论
class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)  # 评论id
    content = db.Column(db.Text)  # 评论内容
    movie_id = db.Column(db.Integer, db.ForeignKey('video.id'))  # 评论所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 评论所属用户
    add_time = db.Column(db.DateTime, index=True, default=datetime.now())  # 评论添加时间


# 收藏
class Favorite(db.Model):
    __tablename__ = "favorite"
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('video.id'))  # 收藏所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 收藏所属用户


# 权限
class Auth(db.Model):
    __tablename__ = "auth"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)  # 权限名称
    url = db.Column(db.String(255), unique=True)  # 权限url
    add_time = db.Column(db.DateTime, index=True, default=datetime.now())  # 添加时间


# 角色
class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)  # 名称
    auths = db.Column(db.String(255))  # 权限列表
    add_time = db.Column(db.DateTime, index=True, default=datetime.now())  # 添加时间


# 管理员
class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)  # 账号
    pwd = db.Column(db.String(100))  # 密码
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # 所属角色
    add_time = db.Column(db.DateTime, index=True, default=datetime.now())  # 添加时间
    adminlogs = db.relationship('Adminlog', backref="admin")  # 管理员日志外键关联
    oplogs = db.relationship('Oplog', backref="admin")  # 操作日志外键关联


# 登录日志
class Adminlog(db.Model):
    __tablename__ = "adminlog"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))  # 所属用户(通过外键与user表相关联)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now())  # 登陆时间，默认为当前时间


# 操作日志

class Oplog(db.Model):
    __tablename__ = "oplog"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))  # 所属管理员(通过外键与user表相关联)
    add_time = db.Column(db.DateTime, index=True, default=datetime.now())  # 登陆时间，默认为当前时间
    option_content = db.Column(db.String(255))  # 操作内容


# 点赞记录
class Zan_records(db.Model):
    __tablename__ = "zan_records"
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, nullable=False)
    zan_user_id = db.Column(db.Text, nullable=False)


# 收藏记录
class Fav_records(db.Model):
    __tablename__ = "fav_records"
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, nullable=False)
    fav_user_id = db.Column(db.Text, nullable=False)


if __name__ == '__main__':
    db.create_all()

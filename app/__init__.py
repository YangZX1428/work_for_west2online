from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.debug = True
class Config():
    SECRET_KEY = "asdasda"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:4343594.@127.0.0.1:3306/myweb"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAX_CONTENT_LENGTH = 40*1024*1024
    SQLALCHEMY_POOL_SIZE = 1024
    SQLALCHEMY_POOL_TIMEOUT = 90
    SQLALCHEMY_POOL_RECYCLE = 3
    SQLALCHEMY_MAX_OVERFLOW = 1024


app.config.from_object(Config)
db = SQLAlchemy(app)
# 导入两个定义好的蓝图对象
from app.home import home as hb
from app.admin import admin as ab

app.register_blueprint(hb)  # 注册前台程序的蓝图

app.register_blueprint(ab, url_prefix="/admin")  # 注册后台程序的蓝图，加上url前缀



# coding:utf8
from datetime import timedelta
from flask_cors import CORS
from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from flask_sqlalchemy import BaseQuery as _BaseQuery
from contextlib import contextmanager

import pymysql, os


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


class BaseQuery(_BaseQuery):
    def fliter_by(self, **kwargs):
        new_kwargs = {}
        for k, v in kwargs.items():
            if v is not None:
                new_kwargs[k] = v
        print(kwargs)
        return super(BaseQuery, self).filter(**new_kwargs)  # 返回父类的fliter_by的执行


# 数据库的配置变量
HOSTNAME = '127.0.0.1'
PORT = '10306'
DATABASE = 'movie'
USERNAME = 'root'
PASSWORD = '123456'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = True
app.config["SECRET_KEY"] = "123456"
app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/upload/')
app.config['SESSION_KEY'] = os.urandom(24)
# app.config['SESSION_COOKIE_NAME']=os.urandom(24)  #这是配置网页中sessions显示的key
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hour=7)  # 配置20秒有效
app.debug = True
db = SQLAlchemy(app, query_class=BaseQuery, session_options={"expire_on_commit": False})
# db = _SQLAlchemy(app)

from app.home import home as home_blueprint

from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)

CORS(app, supports_credentials=True)


app.register_blueprint(admin_blueprint, url_prefix="/admin")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("home/404.html"), 404

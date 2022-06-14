# coding:utf8
import json
from datetime import datetime
from app import db
import html


# 会员
class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    pwd = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(11), unique=True)
    info = db.Column(db.Text)
    face = db.Column(db.String(255))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    status = db.Column(db.Integer, default=1)  # -1代表封号，0代表禁言，1代表正常
    # uuid = db.Column(db.String(255), unique=True)  # 唯一标识符
    userlogs = db.relationship('Userlog', backref='user')  # 会员日志外键关联
    comments = db.relationship('Comment', backref='user')  # 外键关联
    history = db.relationship('History', backref='user')  # 外键关联
    # user_history_movie = db.relationship("Movie", backref="user", secondary="history")  # 电影 外键关联


    def check_pwd(self, pwd):
        return self.pwd == pwd

    def __repr__(self):
        return "<User %r>" % self.name


# 会员登录日志
class Userlog(db.Model):
    __tablename__ = "userlog"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属会员
    ip = db.Column(db.String(100))  # ip
    time = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Userlog %r>" % self.id


# 标签
class Tag(db.Model):
    __tablename__ = "tag"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    tagId = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(100))
    movies = db.relationship("Movie", backref="tag", secondary="movie_tag")  # 电影 外键关联

    def __repr__(self):
        return "<tag %r>" % self.tag

# 电影-标签
class movie_tag(db.Model):
    __tablename__ = "movie_tag"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    movieId = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key=True)
    tagId = db.Column(db.Integer, db.ForeignKey('tag.tagId'), primary_key=True)
    relevance = db.Column(db.Float, primary_key=False)


    def __repr__(self):
        return {'movieId': self.movieId, 'tagId': self.tagId, 'relevance': self.relevance}

#  电影
class Movie(db.Model):
    __tablename__ = "movie"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255))
    urlId = db.Column(db.String(255))
    storyline = db.Column(db.Text)
    poster = db.Column(db.String(255))
    playnum = db.Column(db.BigInteger)  # 播放量
    commentnum = db.Column(db.BigInteger)
    lang = db.Column(db.String(255))
    duration = db.Column(db.Integer)
    genres = db.Column(db.String(255))
    rate = db.Column(db.Float)
    actors = db.Column(db.String(255))
    year = db.Column(db.Integer)
    web_name = db.Column(db.String(255))
    comments = db.relationship('Comment', backref='movie')  # 外键关联
    history = db.relationship('History', backref='movie')  # 外键关联
    # movieId = db.relationship('movie_tag', backref='movie')
    # user = db.relationship("User", backref=db.backref('movie'), secondary="comment")  # 电影 外键关联

    def __repr__(self):
        # return "<Movie %r>" % self.title
        return json.dumps({'title': self.title, 'urlId': self.urlId, 'storyline': self.storyline,
                           'poster': self.poster, 'playnum': self.playnum, 'commentnum': self.commentnum,
                           'lang': self.lang, 'duration': self.duration,
                           'genres': self.genres, 'rate': self.rate, 'actors': self.actors, 'year': self.year,
                           'web_name': self.web_name, 'id': self.id}, ensure_ascii=False)


# #  电影
# class Movie_info(db.Model):
#     __tablename__ = "movie_info"
#     __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
#     movie_id = db.Column(db.Integer, primary_key=True)  # 编号
#     title = db.Column(db.String(255))
#     web_id = db.Column(db.String(255))
#     image_url = db.Column(db.String(255))
#     web_name = db.Column(db.String(255))
#     actors = db.Column(db.String(255))
#     year = db.Column(db.Integer)
#     rate = db.Column(db.Float)
#     storyline = db.Column(db.Text)
#     language = db.Column(db.String)
#     duration = db.Column(db.Integer)
#     genres = db.Column(db.String)
#
#     def __repr__(self):
#         # if self.web_name:
#         #     return "<Movie_info %r>" % self.web_name
#         # else:
#         #     return "<Movie_info %r>" % self.title
#
#         return json.dumps(
#             {'movie_id': self.movie_id, 'title': self.title, 'web_id': self.web_id, 'image_url': self.image_url,
#              'web_name': self.web_name, 'actors': self.actors, 'year': self.year, 'rate': self.rate,
#              'storyline': self.storyline, 'language': self.language, 'duration': self.duration, 'genres': self.genres})
#

#  上映预告
class Preview(db.Model):
    __tablename__ = "preview"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255), unique=True)
    logo = db.Column(db.String(255), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Preview %r>" % self.title


# 评论
class Comment(db.Model):
    __tablename__ = "comment"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    edittime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Comment %r>" % self.id


# 电影历史
class History(db.Model):
    __tablename__ = "history"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<history %r>" % self.id


# 权限
class Auth(db.Model):
    __tablename__ = "auth"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(255), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Auth %r>" % self.name


# 角色
class Role(db.Model):
    __tablename__ = "role"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    auths = db.Column(db.String(600), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Role %r>" % self.name


# 管理员
class Admin(db.Model):
    __tablename__ = "admin"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    pwd = db.Column(db.String(100))
    is_super = db.Column(db.SmallInteger)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    adminlogs = db.relationship('Adminlog', backref='admin')  # 外键关联
    oplogs = db.relationship('Oplog', backref='admin')  # 外键关联

    def __repr__(self):
        return "<Admin %r>" % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        print(self.pwd)
        return self.pwd == pwd


# 管理员登录日志
class Adminlog(db.Model):
    __tablename__ = "adminlog"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属会员
    ip = db.Column(db.String(100))  # ip
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<adminlog %r>" % self.id


# 操作日志

class Oplog(db.Model):
    __tablename__ = "Oplog"
    __table_args__ = {"extend_existing": True}  # 如果表已经被创建过,需要加这个参数提供扩展
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属会员
    ip = db.Column(db.String(100))  # ip
    reason = db.Column(db.String(600))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Oplog %r>" % self.id

# if __name__ == "__main__":
#     # db.create_all()
#     role = Role(
#         name="超级管理员",
#         auths=""
#     )
#     db.session.add(role)
#
#     db.session.commit()
#     from werkzeug.security import generate_password_hash
#
#     admin = Admin(
#         name="li",
#         pwd=generate_password_hash("123546"),
#         is_super=0,
#         role_id=1
#     )
#
#     db.session.add(admin)
#     db.session.commit()

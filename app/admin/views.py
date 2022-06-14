# coding:utf8
import json
import re
import time

from . import admin
from flask import render_template, redirect, url_for, flash, session, request, jsonify, make_response
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm
from app.models import Admin, Tag, Movie, Preview, User, Comment
# from app.admin.forms import LoginForm, TagForm, MovieForm
# from app.models import Admin, Tag, Movie
import resource

from functools import wraps
from app import db, app
from werkzeug.utils import secure_filename
import os, datetime, uuid

SESSION_IDS = {}
LOGIN_TIMEOUT = 60 * 60 * 7  # 7 hours


def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@admin.route("/")
def index():
    session_id = request.cookies.get('session_id')
    if session_id == None:
        resp = make_response(render_template("admin/login.html"))
        resp.set_cookie('session_id', os.urandom(37).hex())
        return resp
    if session_id not in SESSION_IDS.keys():
        pass
    elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
    else:
        SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
        # return render_template("home/index.html")
        return render_template("admin/index.html", admin=SESSION_IDS[session_id]['admin'])
    return redirect(url_for("admin.login"))


@admin.route("/mem", methods=["GET", "POST"])
def mem():
    try:
        mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        print(mem_usage)
        return jsonify({"code": 200, "mem_usage": mem_usage})
    except Exception as e:
        print(e)
        return jsonify({"code": 500, "msg": "服务器错误"})


@admin.route("/login/", methods=["GET", "POST"])
def login():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    if session_id == None:
        resp = make_response(render_template("admin/login.html"))
        resp.set_cookie('session_id', os.urandom(37).hex())
        return resp
    if session_id not in SESSION_IDS.keys():
        pass
    elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
    else:
        SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
        # return render_template("home/index.html")
        return render_template("admin/index.html", admin=SESSION_IDS[session_id]['admin'])
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误！")
            print(data["pwd"])
            return render_template("admin/login.html", form=form)
        SESSION_IDS[session_id] = {'timestamp': time.time(), 'admin': admin}
        return render_template("admin/index.html", admin=admin)
    return render_template("admin/login.html", form=form)



@admin.route("/logout/")
def logout():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    try:
        SESSION_IDS.pop(session_id)
    except:
        pass
    # session.pop('admin', None)
    # print(session)
    return redirect(url_for("admin.login"))


@admin.route("/pwd/", methods=["GET", "POST"])
def pwd():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    if session_id == None:
        resp = make_response(render_template("admin/login.html"))
        resp.set_cookie('session_id', os.urandom(37).hex())
        return resp
    if session_id not in SESSION_IDS.keys():
        return redirect(url_for("admin.login"))
    elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
        return redirect(url_for("admin.login"))
    else:
        SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间

    try:
        data = request.get_data()
        data = json.loads(data)
        print(data)
        new_pwd = data['new']
        old_pwd = data['old']
        action = data['action']
        admin = Admin.query.filter(Admin.id == SESSION_IDS[session_id]['admin'].id).first()
        if action == 'change_pwd':
            if old_pwd is not old_pwd:
                return jsonify({"code": 400, "msg": "旧密码错误"})
            admin.pwd = new_pwd
            db.session.commit()
            return jsonify({"code": 200, "msg": "修改成功"})
        return jsonify({"code": 500, "msg": "パラメータエラー！ あほう！"})
    except Exception as e:
        print(e)
        return render_template("admin/pwd.html", admin=SESSION_IDS[session_id]['admin'])


# #  添加标签
# @admin.route("/tag/add/", methods=["GET", "POST"])
# @admin_login_req
# def tag_add():
#     global SESSION_IDS
#     session_id = request.cookies.get('session_id')
#     if session_id == None:
#         resp = make_response(render_template("admin/login.html"))
#         resp.set_cookie('session_id', os.urandom(37).hex())
#         return resp
#     if session_id not in SESSION_IDS.keys():
#         return redirect(url_for("admin.login"))
#     elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
#         SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
#         return redirect(url_for("admin.login"))
#     else:
#         SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
#     form = TagForm()
#     if form.validate_on_submit():
#         data = form.data
#         tag = Tag.query.filter_by(name=data["name"]).count()
#         if tag == 1:
#             flash("名称已经存在！", "err")
#             return redirect(url_for("admin.tag_add"))
#         tag = Tag(
#             name=data["name"]
#         )
#         db.session.add(tag)
#         db.session.commit()
#         flash("添加标签成功！", "ok")
#         redirect(url_for("admin.tag_add"))
#     print(form.name.errors)
#     return render_template("admin/tag_add.html", form=form)


# # 标签列表
# @admin.route("/tag/list/<int:page>/", methods=["GET"])
# @admin_login_req
# def tag_list(page=None):
#     global SESSION_IDS
#     session_id = request.cookies.get('session_id')
#     if session_id == None:
#         resp = make_response(render_template("admin/login.html"))
#         resp.set_cookie('session_id', os.urandom(37).hex())
#         return resp
#     if session_id not in SESSION_IDS.keys():
#         return redirect(url_for("admin.login"))
#     elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
#         SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
#         return redirect(url_for("admin.login"))
#     else:
#         SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
#
#     if page is None:
#         page = 1
#     page_data = Tag.query.order_by(
#         Tag.addtime.desc()
#     ).paginate(page=page, per_page=10)
#     return render_template("admin/tag_list.html", page_data=page_data)


# # 标签删除
# @admin.route("/tag/del/<int:id>/", methods=["GET"])
# @admin_login_req
# def tag_del(id=None):
#     global SESSION_IDS
#     session_id = request.cookies.get('session_id')
#     if session_id == None:
#         resp = make_response(render_template("admin/login.html"))
#         resp.set_cookie('session_id', os.urandom(37).hex())
#         return resp
#     if session_id not in SESSION_IDS.keys():
#         return redirect(url_for("admin.login"))
#     elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
#         SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
#         return redirect(url_for("admin.login"))
#     else:
#         SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
#
#     print(id)
#     tag = Tag.query.filter_by(id=id).first_or_404()
#     db.session.delete(tag)
#     db.session.commit()
#     flash("删除标签成功!", "ok")
#     return redirect(url_for('admin.tag_list', page=1))


# #  编辑标签
# @admin.route("/tag/edit/<int:id>", methods=["GET", "POST"])
# @admin_login_req
# def tag_edit(id=None):
#     global SESSION_IDS
#     session_id = request.cookies.get('session_id')
#     if session_id == None:
#         resp = make_response(render_template("admin/login.html"))
#         resp.set_cookie('session_id', os.urandom(37).hex())
#         return resp
#     if session_id not in SESSION_IDS.keys():
#         return redirect(url_for("admin.login"))
#     elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
#         SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
#         return redirect(url_for("admin.login"))
#     else:
#         SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
#
#     form = TagForm()
#     tag = Tag.query.get_or_404(id)
#     if form.validate_on_submit():
#         data = form.data
#         tag_count = Tag.query.filter_by(name=data["name"]).count()
#         print(data["name"])
#         if tag.name != data["name"] and tag_count == 1:
#             flash("名称已经存在！", "err")
#             return redirect(url_for("admin.tag_edit", id=id))
#         tag.name = data["name"]
#         db.session.add(tag)
#         db.session.commit()
#         flash("修改标签成功！", "ok")
#         return redirect(url_for("admin.tag_edit", id=id))
#     return render_template("admin/tag_edit.html", form=form, tag=tag)


# @admin.route("/movie/add/", methods=["GET", "POST"])
# @admin_login_req
# def movie_add():
#     global SESSION_IDS
#     session_id = request.cookies.get('session_id')
#     if session_id == None:
#         resp = make_response(render_template("admin/login.html"))
#         resp.set_cookie('session_id', os.urandom(37).hex())
#         return resp
#     if session_id not in SESSION_IDS.keys():
#         return redirect(url_for("admin.login"))
#     elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
#         SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
#         return redirect(url_for("admin.login"))
#     else:
#         SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
#
#     form = MovieForm()
#     if form.validate_on_submit():
#         data = form.data
#         file_url = secure_filename(form.url.data.filename)
#         logo_url = secure_filename(form.logo.data.filename)
#         if not os.path.exists(app.config["UP_DIR"]):
#             os.makedirs(app.config["UP_DIR"])
#             os.chmod(app.config["UP_DIR"], "rw")
#         url = change_filename(file_url)
#         logo = change_filename(logo_url)
#         form.url.data.save(app.config["UP_DIR"] + url)
#         form.logo.data.save(app.config["UP_DIR"] + logo)
#
#         movie = Movie(
#             title=data["title"],
#             url=url,
#             info=data["info"],
#             logo=logo,
#             star=int(data["star"]),
#             playnum=0,
#             commentnum=0,
#             tag_id=int(data["tag_id"]),
#             release_time=data["release_time"],
#             length=data["length"],
#         )
#         db.session.add(movie)
#         db.session.commit()
#         flash("添加电影成功!", "ok")
#         return redirect(url_for("admin.movie_add"))
#     return render_template("admin/movie_add.html", form=form)


@admin.route("/movie/list", methods=["GET"])
def movie_list():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    if session_id == None:
        resp = make_response(render_template("admin/login.html"))
        resp.set_cookie('session_id', os.urandom(37).hex())
        return resp
    if session_id not in SESSION_IDS.keys():
        return redirect(url_for("admin.login"))
    elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
        return redirect(url_for("admin.login"))
    else:
        SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间

    page = request.args.get('page')
    key = request.args.get('key')

    movies = Movie.query
    if key:
        key = key.split(' ')
        keys = []
        for i in key:
            result = re.sub(r'\(.*\)|[^\s|\w\']|\d', '', i).lower()
            if result:
                keys.append(str(result))
        print(keys)
        for i in keys:
            movies = movies.filter(Movie.title.like('%' + i + '%'))

    try:
        if page is None:
            page = 1
        else:
            page = int(page)
    except:
        page = 1

    num = movies.count()
    remain = int(num % 20 > 0)
    num = num // 20 + remain
    if page > num:
        page = num
    if page <= 0:
        page = 1
    movies_list = movies.offset((page - 1) * 20).limit(20).all()

    return render_template("admin/movie_list.html", movies=movies_list, admin=SESSION_IDS[session_id]['admin'], num=num,
                           page=page)


# @admin.route("/movie/del/<int:id>/", methods=["GET"])
# @admin_login_req
# def movie_del(id=None):
#     global SESSION_IDS
#     session_id = request.cookies.get('session_id')
#     if session_id == None:
#         resp = make_response(render_template("admin/login.html"))
#         resp.set_cookie('session_id', os.urandom(37).hex())
#         return resp
#     if session_id not in SESSION_IDS.keys():
#         return redirect(url_for("admin.login"))
#     elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
#         SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
#         return redirect(url_for("admin.login"))
#     else:
#         SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
#
#     movie = Movie.query.filter_by(id=id).first_or_404()
#     db.session.delete(movie)
#     db.session.commit()
#     flash("删除电影成功!", "ok")
#     return redirect(url_for('admin.movie_list', page=1))


@admin.route("/movie/edit/<int:id>", methods=["GET", "POST"])
def movie_edit(id=None):
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    if session_id == None:
        resp = make_response(render_template("admin/login.html"))
        resp.set_cookie('session_id', os.urandom(37).hex())
        return resp
    if session_id not in SESSION_IDS.keys():
        return redirect(url_for("admin.login"))
    elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
        return redirect(url_for("admin.login"))
    else:
        SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间

    form = MovieForm()
    # form.url.validators = []
    # form.logo.validators = []
    movie = Movie.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        movie_count = Movie.query.filter_by(title=data["title"]).count()
        if movie.title != data["title"] and movie_count == 1:
            flash("名称已经存在！", "err")
            return redirect(url_for("admin.movie_edit", id=id))

        # if not os.path.exists(app.config["UP_DIR"]):
        #     os.makedirs(app.config["UP_DIR"])
        #     os.chmod(app.config["UP_DIR"], "rw")

        # if form.url.data.filename != "":
        #     file_url = secure_filename(form.url.data.filename)
        #     movie.url = change_filename(file_url)
        #     form.url.data.save(app.config["UP_DIR"] + movie.url)
        # if form.logo.data.filename != "":
        #     logo_url = secure_filename(form.logo.data.filename)
        #     movie.logo = change_filename(logo_url)
        #     form.logo.data.save(app.config["UP_DIR"] + movie.logo)
        # movie.storyline = data["info"]
        movie.title = data["title"]
        movie.lang = data["lang"]
        movie.length = data["length"]
        movie.year = data["release_time"]
        db.session.add(movie)
        db.session.commit()
        flash("修改电影成功！", "ok")
        return redirect(url_for("admin.movie_edit", id=id))
    return render_template("admin/movie_edit.html", form=form, movie=movie, admin=SESSION_IDS[session_id]['admin'])


#
#
# @admin.route("/preview/add/", methods=["GET", "POST"])
# @admin_login_req
# def preview_add():
#     global SESSION_IDS
#     session_id = request.cookies.get('session_id')
#     if session_id == None:
#         resp = make_response(render_template("admin/login.html"))
#         resp.set_cookie('session_id', os.urandom(37).hex())
#         return resp
#     if session_id not in SESSION_IDS.keys():
#         return redirect(url_for("admin.login"))
#     elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
#         SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
#         return redirect(url_for("admin.login"))
#     else:
#         SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
#
#     form = PreviewForm()
#     if form.validate_on_submit():
#         data = form.data
#         logo_url = secure_filename(form.logo.data.filename)
#         if not os.path.exists(app.config["UP_DIR"]):
#             os.makedirs(app.config["UP_DIR"])
#             os.chmod(app.config["UP_DIR"], "rw")
#         logo = change_filename(logo_url)
#         form.logo.data.save(app.config["UP_DIR"] + logo)
#     return render_template("admin/preview_add.html", form=form)


# @admin.route("/preview/list/")
# @admin_login_req
# def preview_list():
#     global SESSION_IDS
#     session_id = request.cookies.get('session_id')
#     if session_id == None:
#         resp = make_response(render_template("admin/login.html"))
#         resp.set_cookie('session_id', os.urandom(37).hex())
#         return resp
#     if session_id not in SESSION_IDS.keys():
#         return redirect(url_for("admin.login"))
#     elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
#         SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
#         return redirect(url_for("admin.login"))
#     else:
#         SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
#
#     return render_template("admin/preview_list.html")


@admin.route("/user/list/")
def user_list():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    if session_id == None:
        resp = make_response(render_template("admin/login.html"))
        resp.set_cookie('session_id', os.urandom(37).hex())
        return resp
    if session_id not in SESSION_IDS.keys():
        return redirect(url_for("admin.login"))
    elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
        return redirect(url_for("admin.login"))
    else:
        SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间

    page = request.args.get('page')

    users = User.query
    try:
        if page is None:
            page = 1
        else:
            page = int(page)
    except:
        page = 1

    num = users.count()
    remain = int(num % 20 > 0)
    num = num // 20 + remain
    if page > num:
        page = num
    if page <= 0:
        page = 1
    user_list = users.offset((page - 1) * 20).limit(20).all()
    print(user_list)

    return render_template("admin/user_list.html", users=user_list, admin=SESSION_IDS[session_id]['admin'], num=num,
                           page=page)


@admin.route("/user/status/", methods=["POST"])
def user_status():
    try:
        global SESSION_IDS
        session_id = request.cookies.get('session_id')
        if session_id == None:
            return jsonify({"code": 400, "msg": "请先登录"})
        if session_id not in SESSION_IDS.keys():
            return jsonify({"code": 404, "msg": "请先登录"})
        elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
            SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
            return jsonify({"code": 400, "msg": "请登录验证"})
        else:
            SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间

        data = request.get_data()
        data = json.loads(data)
        print(data)
        user_id = data['user_id']
        action = data['action']
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"code": 400, "msg": "用户不存在"})
        if action == 'status':
            user.status = data['status']
            db.session.commit()
            return jsonify({"code": 200, "msg": "修改成功"})
        elif action == 'delete':
            print(action)
            # db.session.delete(user)
            # db.session.commit()
            return jsonify({"code": 200, "msg": "删除成功"})
        return jsonify({"code": 500, "msg": "パラメータエラー！ あほう！"})
    except Exception as e:
        print(e)
        return jsonify({"code": 500, "msg": "パラメータエラー！ あほう！"})


# @admin.route("/user/view/")
# @admin_login_req
# def user_view():
#     global SESSION_IDS
#     session_id = request.cookies.get('session_id')
#     if session_id == None:
#         resp = make_response(render_template("admin/login.html"))
#         resp.set_cookie('session_id', os.urandom(37).hex())
#         return resp
#     if session_id not in SESSION_IDS.keys():
#         return redirect(url_for("admin.login"))
#     elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
#         SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
#         return redirect(url_for("admin.login"))
#     else:
#         SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
#
#     return render_template("admin/user_view.html", admin=SESSION_IDS[session_id]['admin'])


@admin.route("/comment/list/")
def comment_list():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    if session_id == None:
        resp = make_response(render_template("admin/login.html"))
        resp.set_cookie('session_id', os.urandom(37).hex())
        return resp
    if session_id not in SESSION_IDS.keys():
        return redirect(url_for("admin.login"))
    elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
        return redirect(url_for("admin.login"))
    else:
        SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间

    page = request.args.get('page')

    comments = Comment.query
    try:
        if page is None:
            page = 1
        else:
            page = int(page)
    except:
        page = 1

    num = comments.count()
    remain = int(num % 7 > 0)
    num = num // 7 + remain
    if page > num:
        page = num
    if page <= 0:
        page = 1
    comments = comments.offset((page - 1) * 7).limit(7).all()
    print(comments)

    return render_template("admin/comment_list.html", admin=SESSION_IDS[session_id]['admin'], comments=comments, num=num, page=page)

@admin.route("/comment/op/", methods=["POST"])
def comment_op():
    try:
        global SESSION_IDS
        session_id = request.cookies.get('session_id')
        if session_id == None:
            return jsonify({"code": 400, "msg": "请先登录"})
        if session_id not in SESSION_IDS.keys():
            return jsonify({"code": 404, "msg": "请先登录"})
        elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
            SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
            return jsonify({"code": 400, "msg": "请登录验证"})
        else:
            SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间

        data = request.get_data()
        data = json.loads(data)
        print(data)
        comment_id = data['comment_id']
        action = data['action']
        comment = Comment.query.get(comment_id)
        if comment is None:
            return jsonify({"code": 400, "msg": "评论不存在"})
        if action == 'delete':
            print(action)
            db.session.delete(comment)
            db.session.commit()
            return jsonify({"code": 200, "msg": "删除成功"})
        else:
            return jsonify({"code": 500, "msg": "パラメータエラー！ あほう！"})
    except Exception as e:
        print(e)
        return jsonify({"code": 500, "msg": "パラメータエラー！ あほう！"})



# @admin.route("/moviecol/list/")
# @admin_login_req
# def moviecol_list():
#     global SESSION_IDS
#     session_id = request.cookies.get('session_id')
#     if session_id == None:
#         resp = make_response(render_template("admin/login.html"))
#         resp.set_cookie('session_id', os.urandom(37).hex())
#         return resp
#     if session_id not in SESSION_IDS.keys():
#         return redirect(url_for("admin.login"))
#     elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
#         SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
#         return redirect(url_for("admin.login"))
#     else:
#         SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
#
#     return render_template("admin/moviecol_list.html")


# @admin.route("/oplog/list/")
# @admin_login_req
# def oplog_list():
#     return render_template("admin/oplog_list.html")
#
#
# @admin.route("/adminloginlog/list/")
# @admin_login_req
# def adminloginlog_list():
#     return render_template("admin/adminloginlog_list.html")
#
#
# @admin.route("/userloginlog/list/")
# @admin_login_req
# def userloginlog_list():
#     return render_template("admin/userloginlog_list.html")
#
#
# @admin.route("/auth/add/")
# @admin_login_req
# def auth_add():
#     return render_template("admin/auth_add.html")
#
#
# @admin.route("/auth/list/")
# @admin_login_req
# def auth_list():
#     return render_template("admin/auth_list.html")
#
#
# @admin.route("/role/add/")
# @admin_login_req
# def role_add():
#     return render_template("admin/role_add.html")
#
#
# @admin.route("/role/list/")
# @admin_login_req
# def role_list():
#     return render_template("admin/role_list.html")
#
#
# @admin.route("/admin/add/")
# @admin_login_req
# def admin_add():
#     return render_template("admin/admin_add.html")
#
#
# @admin.route("/admin/list/")
# @admin_login_req
# def admin_list():
#     return render_template("admin/admin_list.html")

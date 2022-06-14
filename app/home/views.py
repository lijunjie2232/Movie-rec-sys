# coding:utf8
import json
import os
import random
import time

from . import home
from flask import render_template, redirect, url_for, request, jsonify, session, make_response
from app.models import Movie, User, Comment, History, Userlog
from hashlib import md5
import string
from app import db

import pandas as pd
import numpy as np
import torch
from app.comm.NCF import NCF

import re
import html

SESSION_IDS = {}
LOGIN_TIMEOUT = 60 * 60 * 7  # 7 hours
samples = None
all_movieIds = None
train_rating = None
model = None
LOG = True
SP_NUM = 7
REC = True
REC_NUM = 3
ITEM_NUM = 57


@home.route("/load")
def load():
    try:
        global samples
        global all_movieIds
        global train_rating
        global model
        global REC_NUM
        global ITEM_NUM
        if REC:
            print('Random predict data generating ...')
            r_num = random.sample(range(0, 17), SP_NUM)
            samples = []
            for i in r_num:
                samples.append(
                    pd.read_csv(
                        './app/comm/output/predict_user_item_sample/predict_usage_data_random_sample_%s.csv' % i))
            # print(samples)
            print('Random predict data generated')

            print('Torch model loading ...')
            all_movieIds = np.loadtxt("./app/comm/output/all_movieIds.csv", dtype="int")
            # print(len(all_movieIds))
            train_rating = pd.read_csv('./app/comm/output/train_rating.csv')
            model = NCF(138491, 131261, train_rating, all_movieIds)
            model.load_state_dict(torch.load('./app/comm/output/model_state.pt'))
            print('Torch model loaded')
            return jsonify({'code': 200, 'msg': 'predict model load successfully'})
        else:
            print('Closing predict model ...')
            samples = None
            all_movieIds = None
            train_rating = None
            model = None
            print('Model closed successfully')
            return jsonify({'code': 200, 'msg': 'predict model cloased successfully'})
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'msg': 'predict model load failed'})


@home.route("/params_set", methods=['GET', 'POST'])
def set_global_params():
    log = False
    sp_num = 7
    rec = False
    login_timeout_hour = 7
    rec_num = 3
    item_num = 57
    try:
        global LOG
        global REC
        global SP_NUM
        global LOGIN_TIMEOUT
        global REC_NUM
        global ITEM_NUM
        data = json.loads(request.get_data())
        if 'log' in data.keys():
            log = data['log']
            if log == 'True':
                log = True
            else:
                log = False
        if 'sp_num' in data.keys():
            sp_num = data['sp_num']
        if 'rec' in data.keys():
            rec = data['rec']
            if rec == 'True':
                rec = True
            else:
                rec = False
        if 'login_timeout_hour' in data.keys():
            login_timeout_hour = data['login_timeout_hour']
        assert login_timeout_hour > 0
        if 'rec_num' in data.keys():
            rec_num = data['rec_num']
        if 'item_num' in data.keys():
            item_num = data['item_num']
        assert item_num >= 8
        assert sp_num <= 17 and sp_num >= 1 and sp_num >= rec_num
        LOG = log
        if LOG:
            print('log is on')
        else:
            print('log is off')
        REC = rec
        if REC:
            print('rec is on')
        else:
            print('rec is off')
        SP_NUM = sp_num
        LOGIN_TIMEOUT = 60 * 60 * login_timeout_hour
        REC_NUM = rec_num
        ITEM_NUM = item_num
        load()
        return jsonify({'code': 200, 'msg': 'set global params success'})
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'msg': 'パラメータエラー！ あほう！'})


@home.route("/login/", methods=["GET", "POST"])
def login():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    if session_id == None:
        resp = make_response(render_template("home/login.html"))
        resp.set_cookie('session_id', os.urandom(37).hex())
        return resp
    print(session_id)
    if session_id not in SESSION_IDS.keys():
        pass
    elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
    else:
        SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
        # return render_template("home/index.html")
        return redirect(url_for("home.index"))

    data = request.get_data()
    try:
        if data == b'':
            return render_template("home/login.html")
        else:
            data = json.loads(data)
            print(data)
            if data['flag'] == 'loginin':
                print('signin')
                email = data['n']
                password = md5(data['p'].encode('utf-8')).hexdigest()
                user = User.query.filter(User.email == email or User.phone == email).first()
                if user:
                    print(type(user))
                    print(user)
                    print(user.pwd)
                    if user.check_pwd(password):
                        if user.status + 1:
                            SESSION_IDS[session_id] = {'user': user, 'timestamp': time.time()}
                            if LOG:
                                ip = request.remote_addr
                                userlog = Userlog(user_id=user.id, ip=ip)
                                db.session.add(userlog)
                                db.session.commit()
                            return jsonify({'code': 200, 'msg': '良いですね!'})
                        else:
                            return jsonify({'code': 404, 'msg': 'あなたのアカウントは停止されています！'})
                    else:
                        return jsonify({'code': 401, 'msg': 'パスワードが違います!'})
                else:
                    return jsonify({'code': 400, 'msg': 'ユーザーは存在しません！'})
            else:
                return jsonify({'code': 500, 'msg': 'パラメータエラー！ あほう！'})
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'msg': 'パラメータエラー！ あほう！'})


@home.route("/logout/")
def logout():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    # if session_id == None:
    #     return redirect(url_for("home.login"))
    #     resp.set_cookie('session_id', os.urandom(37).hex())
    #     return resp

    if session_id in SESSION_IDS.keys():
        SESSION_IDS.pop(session_id)
        # return redirect(url_for("home.login"))
    try:
        route = request.full_path[25:]
        print(route)
        return redirect(url_for("home.index") + route)
    except Exception as e:
        print(e)
        return redirect(url_for("home.login"))
    # return redirect(url_for(""))


@home.route("/register/", methods=["GET", "POST"])
def register():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    if session_id == None:
        resp = make_response(render_template("home/register.html"))
        resp.set_cookie('session_id', os.urandom(37).hex())
        return resp

    global SESSION_IDS
    if session_id not in SESSION_IDS.keys():
        pass
    elif SESSION_IDS[session_id]["timestamp"] - time.time() > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
    else:
        SESSION_IDS[session_id]["timestamp"] = time.time()  # 更新会话时间
        # return render_template("home/index.html")
        return redirect(url_for("home.index"))
    try:
        data = request.get_data()
        if data == b'':
            return render_template("home/register.html")
        else:
            data = json.loads(data)
            print(data)
            if data['flag'] == 'signin':
                print('signin')
                username = data['username']
                password = data['password']
                repassword = data['repassword']
                email = data['email']
                phone = data['phone']

                if not re.match(r"1[0-9]{10}", phone):
                    return jsonify({'code': '400', 'msg': 'Phone number is invalid!'})
                user = User.query.filter(User.phone == phone).first()
                if user:
                    return jsonify({'code': '400', 'msg': 'Phone number is already registered!'})

                mail_set = {
                    'qq.com',
                    '163.com',
                    '126.com',
                    'sina.com',
                    'gmail.com',
                    'hotmail.com',
                    'yahoo.com',
                    'sohu.com',
                    '139.com',
                    '189.com',
                    'wo.com.cn',
                    '189.cn',
                    'tyut.edu.cn',
                    'link.tyut.edu.cn'
                }

                if email.find('@') == -1 and len(email.split('@')) - 1:
                    return jsonify({'code': '400', 'msg': 'Email address is invalid!'})
                    email = input("Please input your email: ")
                if email.split('@')[1] not in mail_set:
                    return jsonify({'code': '400',
                                    'msg': 'Email server is not suported. Please use the common domestic email, support email :163,126,qq,gmail,hotmail,yahoo,sohu,139,189,wo,189.cn,tyut.edu.cn,link.tyut.edu.cn'})

                print(username, password, repassword, email, phone)
                user = User.query.filter(User.email == email).first()
                if user:
                    return jsonify({'code': '400', 'msg': 'Email address is already registered!'})

                if password != repassword:
                    return jsonify({'code': '400', 'msg': 'The two passwords are not matched!'})
                passwordDic = {
                    'dig': string.digits,  # '0123456789'
                    'lower': string.ascii_lowercase,  # 'abcdefghijklmnopqrstuvwxyz'
                    'upper': string.ascii_uppercase,  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    'pun': string.punctuation  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
                }
                d = l = u = p = 0
                if len(password) >= 8:
                    for i in password:
                        if i in passwordDic['dig']:
                            d = 2
                        if i in passwordDic['lower']:
                            l = 2
                        if i in passwordDic['upper']:
                            u = 2
                        if i in passwordDic['pun']:
                            p = 1
                    if d + l + u + p < 4:
                        return jsonify({'code': '400', 'msg': 'Password should contains both digit and letter!'})
                    else:
                        password = md5(password.encode('utf-8')).hexdigest()
                else:
                    return jsonify({'code': '400', 'msg': 'Password should be at least 8 characters!'})

                user = User.query.filter(User.name == username).first()
                if user:
                    return jsonify({'code': '400', 'msg': 'Username already in use!'})

                user = User(name=username, pwd=password, email=email, phone=phone)
                print({'name': username, 'password': password, 'email': email, 'phone': phone})
                db.session.add(user)
                db.session.commit()
                user = User.query.filter(User.email == user.email).first()

                SESSION_IDS[session_id] = {'user': user, 'timestamp': time.time()}

                return jsonify({'code': 200, 'msg': '良いですね'})
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'msg': 'パラメータエラー！ あほう！'})


@home.route("/user/", methods=['GET', 'POST'])
def user():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    if session_id == None:
        # resp = make_response(render_template("home/login.html"))
        # resp.set_cookie('session_id', os.urandom(37).hex())
        # return resp
        return redirect(url_for("home.login") + "?redirectedfrom=user")
    if session_id not in SESSION_IDS.keys():
        return redirect(url_for("home.login") + "?redirectedfrom=user")
    elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
        return redirect(url_for("home.login") + "?redirectedfrom=user")
    else:
        SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
    try:
        data = request.get_data()
        if data == b'':
            return render_template("home/user.html", user=SESSION_IDS[session_id]['user'])
        else:
            data = json.loads(data)
            print(data)
            if data['flag'] == 'change':
                username = data['username']
                email = data['email']
                phone = data['phn']
                intro = data['intro']
                print(intro)

                if SESSION_IDS[session_id]['user'].phone != phone:
                    if not re.match(r"1[0-9]{10}", phone):
                        return jsonify({'code': '400', 'msg': 'Phone number is invalid!'})
                    user = User.query.filter(User.phone == phone).first()
                    if user:
                        return jsonify({'code': '400', 'msg': 'Phone number is already registered!'})

                if SESSION_IDS[session_id]['user'].email != email:
                    mail_set = {
                        'qq.com',
                        '163.com',
                        '126.com',
                        'sina.com',
                        'gmail.com',
                        'hotmail.com',
                        'yahoo.com',
                        'sohu.com',
                        '139.com',
                        '189.com',
                        'wo.com.cn',
                        '189.cn',
                        'tyut.edu.cn',
                        'link.tyut.edu.cn'
                    }

                    if email.find('@') == -1 and len(email.split('@')) - 1:
                        return jsonify({'code': '400', 'msg': 'Email address is invalid!'})
                        email = input("Please input your email: ")
                    if email.split('@')[1] not in mail_set:
                        return jsonify({'code': '400',
                                        'msg': 'Email server is not suported. Please use the common domestic email, support email :163,126,qq,gmail,hotmail,yahoo,sohu,139,189,wo,189.cn,tyut.edu.cn,link.tyut.edu.cn'})

                    user = User.query.filter(User.email == email).first()
                    if user:
                        return jsonify({'code': '400', 'msg': 'Email address is already registered!'})

                if SESSION_IDS[session_id]['user'].name != username:
                    user = User.query.filter(User.name == username).first()
                    if user:
                        return jsonify({'code': '400', 'msg': 'Username already in use!'})

                u = User.query.filter(User.id == SESSION_IDS[session_id]['user'].id).first()
                print(u)
                u.name = username
                u.email = email
                u.phone = phone
                u.info = intro
                db.session.commit()
                SESSION_IDS.pop(session_id)
                return jsonify({'code': 200, 'msg': '良いですね'})
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'msg': 'パラメータエラー！ あほう！'})


@home.route("/pwd/", methods=['GET', 'POST'])
def pwd():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    if session_id == None:
        return redirect(url_for("home.login") + "?redirectedfrom=pwd")
    if session_id not in SESSION_IDS.keys():
        return redirect(url_for("home.login") + "?redirectedfrom=pwd")
    elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
    else:
        SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
    try:
        data = request.get_data()
        if data == b'':
            return render_template("home/pwd.html", user=SESSION_IDS[session_id]['user'])
        else:
            data = json.loads(data)
            print(data)
            if data['flag'] == 'change':
                old_pwd = data['oldpwd']
                new_pwd = data['newpwd']
                new_pwd_confirm = data['repwd']

                if md5(old_pwd.encode('utf-8')).hexdigest() != SESSION_IDS[session_id]['user'].pwd:
                    return jsonify({'code': '400', 'msg': 'Original password is wrong!'})
                elif new_pwd != new_pwd_confirm:
                    return jsonify({'code': '400', 'msg': 'The two passwords are not matched!'})
                passwordDic = {
                    'dig': string.digits,  # '0123456789'
                    'lower': string.ascii_lowercase,  # 'abcdefghijklmnopqrstuvwxyz'
                    'upper': string.ascii_uppercase,  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    'pun': string.punctuation  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
                }
                d = l = u = p = 0
                if len(new_pwd) >= 8:
                    for i in new_pwd:
                        if i in passwordDic['dig']:
                            d = 2
                        if i in passwordDic['lower']:
                            l = 2
                        if i in passwordDic['upper']:
                            u = 2
                        if i in passwordDic['pun']:
                            p = 1
                    if d + l + u + p < 4:
                        return jsonify({'code': '400', 'msg': 'Password should contains both digit and letter!'})
                    else:
                        user = User.query.filter(User.id == SESSION_IDS[session_id]['user'].id).first()
                        user.pwd = md5(new_pwd.encode('utf-8')).hexdigest()
                else:
                    return jsonify({'code': '400', 'msg': 'Password should be at least 8 characters!'})
                db.session.commit()
                SESSION_IDS.pop(session_id)
                return jsonify({'code': '200', 'msg': 'Password changed!'})
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'msg': 'パラメータエラー！ あほう！'})


@home.route("/comments/", methods=['GET', 'POST'])
def comments():
    global SESSION_IDS
    try:
        data = json.loads(request.get_data())
        print(data)
        if data['action'] == 'get_movie_comments':
            movie_id = data['movie_id']
            page = data['page']

            comments = Comment.query.filter(Comment.movie_id == movie_id).order_by(Comment.edittime.desc())

            num = comments.count()
            remain = int(num % 7 > 0)
            num = num // 7 + remain
            print(page, num)
            if page > num:
                page = num
            if page < 1:
                page = 1
            print(page, num)

            comments = comments.offset((page - 1) * 7).limit(7).all()
            comments_list = []
            for comment in comments:
                comments_list.append({'user': comment.user.name, 'content': comment.content,
                                      'timestamp': comment.edittime.strftime("%Y-%m-%d %H:%M")})
            if page > num:
                page = num
            return jsonify(
                {'code': 200, 'msg': 'Get comments successfully', 'comments': comments_list, 'page': page, 'num': num})
        elif data['action'] == 'get_user_comments':
            session_id = request.cookies.get('session_id')
            if session_id == None or session_id not in SESSION_IDS.keys():
                return jsonify({'code': 400, 'msg': 'Please login first'})
            elif SESSION_IDS[session_id]["timestamp"] - time.time() > LOGIN_TIMEOUT:
                SESSION_IDS.pop(session_id)
                return jsonify({'code': 400, 'msg': 'Please login first'})
            else:
                SESSION_IDS[session_id]["timestamp"] = time.time()
                user_id = SESSION_IDS[session_id]['user']['id']
            # user_id = data['user_id']
            comments = Comment.query.filter(Comment.user_id == user_id).all()
            comments_list = []
            for comment in comments:
                comments_list.append({'user_id': comment.user_id, 'content': comment.content,
                                      'timestamp': comment.timestamp})
            return jsonify({'code': 200, 'msg': '获取成功', 'comments': comments_list})
        elif data['action'] == 'add':
            movie_id = data['movie_id']
            user_id = data['user_id']
            content = data['content']
            user = User.query.filter(User.id == user_id).first()
            if user.status == 0:
                return jsonify({'code': 400, 'msg': 'You have been banned from making comments!'})
            comment = Comment(user_id=user_id, movie_id=movie_id, content=content)
            db.session.add(comment)
            db.session.commit()
            return jsonify({'code': 200, 'msg': 'Make comment successfully'})
        elif data['action'] == 'delete':
            comment = Comment.query.filter(Comment.id == data['id']).first()
            db.session.delete(comment)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '删除成功'})
        elif data['action'] == 'update':
            comment = Comment.query.filter(Comment.id == data['id']).first()
            comment.content = data['content']
            db.session.add(comment)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '更新成功'})
        else:
            return jsonify({'code': 400, 'msg': 'なんでもない'})
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'msg': 'パラメータエラー！ あほう！'})


@home.route("/loginlog/")
def loginlog():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    if session_id == None:
        # resp = make_response(render_template("home/login.html"))
        # resp.set_cookie('session_id', os.urandom(37).hex())
        # return resp
        return redirect(url_for("home.login") + "?redirectedfrom=loginlog")
    if session_id not in SESSION_IDS.keys():
        return redirect(url_for("home.login") + "?redirectedfrom=loginlog")
    elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
        return redirect(url_for("home.login") + "?redirectedfrom=loginlog")
    else:
        SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
    page = request.args.get('page')
    if page is None:
        page = 1
    else:
        page = int(page)
    loginlogs = Userlog.query.filter(Userlog.user_id == SESSION_IDS[session_id]['user'].id).order_by(
        Userlog.time.desc())

    num = loginlogs.count()
    remain = int(num % 7 > 0)
    num = num // 7 + remain
    if page > num:
        page = num
    if page <= 0:
        page = 1
    loginlogs = loginlogs.offset((page - 1) * 7).limit(7).all()
    if page > num:
        page = num
    return render_template("home/loginlog.html", loginlogs=loginlogs, page=page, num=num,
                           user=SESSION_IDS[session_id]['user'])

    # return render_template("home/loginlog.html")


@home.route("/history/")
def history():
    global SESSION_IDS
    session_id = request.cookies.get('session_id')
    if session_id == None:
        # resp = make_response(render_template("home/login.html"))
        # resp.set_cookie('session_id', os.urandom(37).hex())
        # return resp
        return redirect(url_for("home.login") + "?redirectedfrom=history")
    if session_id not in SESSION_IDS.keys():
        return redirect(url_for("home.login") + "?redirectedfrom=history")
    elif time.time() - SESSION_IDS[session_id]['timestamp'] > LOGIN_TIMEOUT:  # 是否会话仍有效
        SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
        return redirect(url_for("home.login") + "?redirectedfrom=history")
    else:
        SESSION_IDS[session_id]['timestamp'] = time.time()  # 更新会话时间
    page = request.args.get('page')
    if page is None:
        page = 1
    else:
        page = int(page)
    movies = History.query.filter(History.user_id == SESSION_IDS[session_id]['user'].id).order_by(
        History.addtime.desc()).distinct(History.movie_id)

    num = movies.count()
    remain = int(num % 7 > 0)
    num = num // 7 + remain
    if page > num:
        page = num
    if page <= 0:
        page = 1
    movies_list = movies.offset((page - 1) * 7).limit(7).all()
    if page > num:
        page = num

    return render_template("home/history.html", movielist=movies_list, num=num, page=page,
                           user=SESSION_IDS[session_id]['user'])

    # return render_template("home/login.html")


@home.route("/")
def index():
    global SESSION_IDS
    genre = request.args.get('genre')
    lang = request.args.get('lang')
    year = request.args.get('year')
    hot = request.args.get('hot')
    time = request.args.get('time')
    page = request.args.get('page')
    movies = Movie.query

    if genre:
        movies = movies.filter(Movie.genres.contains([genre]))

    if lang:
        movies = movies.filter(Movie.lang == lang)

    if year:
        year = int(year)
        if year == 1900:
            movies = movies.filter(Movie.year < 1980)
        else:
            movies = movies.filter(Movie.year >= year, Movie.year < year + 10)

    if time == '0':
        movies = movies.order_by(Movie.year.desc())
    elif time == '1':
        movies = movies.order_by(Movie.year.asc())

    if hot == '0':
        movies = movies.order_by(Movie.rate.desc())
    elif hot == '1':
        movies = movies.order_by(Movie.rate.asc())

    if page is None:
        page = 1
    else:
        page = int(page)

    num = movies.count()
    remain = int(num % 20 > 0)
    num = num // 20 + remain
    if page > num:
        page = num
    if page <= 0:
        page = 1
    movies_list = movies.offset((page - 1) * 20).limit(20).all()
    if request.cookies.get('session_id') == None:
        resp = make_response(render_template("home/index.html", page=page, num=num, movieslist=movies_list))
        resp.set_cookie('session_id', os.urandom(37).hex())
        return resp
    session_id = request.cookies.get('session_id')
    user = None
    if session_id in SESSION_IDS:
        user = SESSION_IDS[session_id]['user']
    print(request.full_path)
    return render_template("home/index.html", page=page, num=num, movieslist=movies_list, user=user,
                           route=request.full_path)
    # return render_template("home/index.html", page=page, num=num, movieslist=movies_list)
    # return render_template("home/index.html" ,data = {'movies':movies_list, 'page':page, 'num':num, 'genre':genre, 'year':year, 'hot':hot, 'time':time})


# @home.route("/animation/")
# def animation():
#     return render_template("home/animation.html")


@home.route("/search/")
def search():
    global SESSION_IDS
    param = request.args.get('keys').split(" ")
    page = request.args.get('page')
    if page is None:
        page = 1
    else:
        page = int(page)

    keys = []
    for i in param:
        result = re.sub(r'\(.*\)|[^\s|\w\']|\d', '', i).lower()
        if result:
            keys.append(str(result))
    print(keys)
    movies = Movie.query
    for i in keys:
        movies = movies.filter(Movie.title.like('%' + i + '%'))

    num = movies.count()
    remain = int(num % 20 > 0)
    _num = num // 20 + remain
    if page <= 0:
        page = 1
    if page > num:
        page = num
    # print(num)
    # print(' '.join(param))

    movies_list = movies.offset((page - 1) * 10).limit(10).all()
    # for i in movies_list:
    #     print(html.unescape(i['storyline']))
    # movies_list['storyline'] = html.unescape(movies_list['storyline'])
    # print(movies_list)
    session_id = request.cookies.get('session_id')
    user = None
    if session_id in SESSION_IDS:
        user = SESSION_IDS[session_id]['user']
    return render_template("home/search.html", movielist=movies_list, num=_num, page=page, _num=num,
                           keys=' '.join(param), user=user, route=request.full_path)


@home.route("/play/<id>")
def play(id):
    global SESSION_IDS
    movie = Movie.query
    movie = movie.filter(Movie.id == id).first()
    movie.playnum += 1
    print(movie)
    session_id = request.cookies.get('session_id')
    user = None
    if session_id in SESSION_IDS and time.time() - SESSION_IDS[session_id]['timestamp'] < LOGIN_TIMEOUT:
        user = SESSION_IDS[session_id]['user']
        history = History(user_id=user.id, movie_id=movie.id)
        db.session.add(history)
    db.session.commit()
    return render_template("home/play.html", movie=movie, user=user, route=request.full_path)


@home.route("/rec/")
def predict():
    global SESSION_IDS
    if not REC:
        return json.dumps({'code': 300, 'msg': 'Recommendation function is temporarily closed by administrator'})
    try:
        if samples is None or all_movieIds is None or train_rating is None or model is None:
            load()
            return json.dumps({'code': 300, 'msg': 'System is initializing, please wait a moment'})
        movie_id = request.args.get('id')
        if movie_id:
            movie_id = int(movie_id)
            print(movie_id)
            r = random.sample(range(0, REC_NUM), 1)[0]
            ratings = samples[r]
            # while movie_id not in ratings['movieId']:
            #     r = random.sample(range(0, 7), 1)[0]
            #     ratings = samples[r]

            all = ratings['movieId'].unique()
            movieset = set(all)
            print(len(movieset))
            item_clicked_by_users = ratings.groupby('movieId')['userId'].apply(list).to_dict()
            same_users = list(np.random.choice(list(item_clicked_by_users[movie_id]), ITEM_NUM))

            items = movieset - set([movie_id])
            predictset = set()
            for u in same_users:
                l = model(
                    torch.tensor([u] * len(items)),
                    torch.tensor(list(items))
                )
                l = np.squeeze(l).detach().numpy()
                result = set([list(items)[i] for i in np.argsort(l)[::-1][0:ITEM_NUM].tolist()])
                predictset |= result
            print('rec')
            print(predictset)
            movie_rec_list = random.sample(list(predictset), 8)
            print(movie_rec_list)
            movie = Movie.query.filter(Movie.id.in_(movie_rec_list)).all()
            print(movie)
            return json.dumps({'rec': str(movie), 'code': 200})
        else:
            return json.dumps({'rec': '-1', 'code': 200})
    except Exception as e:
        print(e)
        return json.dumps({'code': 500, 'msg': 'パラメータエラー！ あほう！'})


@home.errorhandler(404)
def page_not_found():
    return render_template("home/404.html"), 404

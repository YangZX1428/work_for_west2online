from . import home
from flask import Flask, request, render_template, redirect, url_for, flash, g
from ..models import User, db, Favorite, Video, Zan_records, Fav_records, Comment, Tag, Admin, Userlog
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
import os
import math
import base64
from .forms import RegistForm, PwdForm, LoginForm, Userinfo, CommentForm, CreateForm
import datetime
import time
import numpy
from redis import StrictRedis

"""
    1.管理员账户: username = yzx， pwd = 123456
    该账户同时也是普通账户
    
    2.未登录时不保存搜索历史记录
    
    3.视频管理界面无收藏点赞或发表评论，添加了删除视频和删除评论的按钮
    
    4.主页面的图片点击后默认进入前四个视频中某一个的视频播放界面
    
    5.视频封面和个人头像若未上传都为默认图片，即default.jpg
    
    
                                        
"""

VIDEO_FOLDER = r"G:\ThirdWork\work_for_west2online\app\static\video"
UPLOAD_FOLDER = r"G:\ThirdWork\work_for_west2online\app\static\faces"
VIDEO_FACE_FOLDER = r"G:\ThirdWork\work_for_west2online\app\static\faces"
TAG_LIST = ["动画", "番剧", "音乐", "舞蹈", "游戏", "科技", "生活", "鬼畜", "时尚", "娱乐", "影视", "广告"]
hasface = 0


def change_time_form(mtime):
    ul_time = time.mktime(mtime.timetuple())
    return str(datetime.datetime.fromtimestamp(ul_time))[0:10]


# 该函数获取该id的视频的评论信息
def get_comment(cs):
    content_list = []  # 评论内容列表
    user_list = []  # 评论用户列表
    time_list = []  # 评论时间列表
    face_list = []
    for c in cs:
        content_list.append(c.content)
        u = User.query.filter_by(id=c.user_id).first()
        user_list.append(u.name)
        time_list.append(change_time_form(c.add_time))
        face_list.append(u.face)
    return content_list, user_list, time_list, face_list


current_user = ""
current_user_name = ""


@home.before_request
def get_g_content():
    global current_user
    global current_user_name
    if current_user == "":
        pass
    else:
        sr = StrictRedis()
        g.search_history = [str(b, encoding="utf-8") for b in sr.lrange(current_user_name, 0, -1)]
        g.key_num = len(sr.lrange(current_user_name, 0, -1))
        g.user = current_user
        g.username = current_user_name


# 登录视图函数
@home.route('/login/<int:code>', methods=["GET", "POST"])
def login(code):
    form = LoginForm()
    if request.method == "GET":
        return render_template('home/login.html', loginform=form, code=code)
    name = form.name.data
    pwd = form.password.data
    global current_user
    global current_user_name
    if form.validate_on_submit():
        if User.query.filter_by(name=name).first() is not None:
            u = User.query.filter_by(name=name).first()
            if pwd == u.password and code == 0 or code > 100:  # 正常登录，登录后跳转到主页面
                # 将用户名和用户对象保存到g容器中
                current_user = User.query.filter_by(name=name).first()
                current_user_name = name
                # 添加登录日志
                user_log = Userlog(user_id=u.id)
                db.session.add(user_log)
                db.session.commit()
                return redirect(url_for("home.user", id=u.id, name=u.name, code=200, page=1))
            elif pwd == u.password and code > 0:  # 登录后跳转到响应视频界面
                # 将用户名和用户对象保存到g容器中
                current_user = User.query.filter_by(name=name).first()
                current_user_name = name
                # 添加登录日志
                user_log = Userlog(user_id=u.id)
                db.session.add(user_log)
                db.session.commit()
                s_name = base64.b64encode(u.name.encode())
                return redirect(url_for("home.play", username=s_name, video_id=code))
            else:
                flash("密码错误!")
        else:
            flash("账号不存在!")
    return render_template('home/login.html', loginform=form)


@home.route('/')
def fisrtpage():
    return redirect(url_for('home.mainpage', page=1))


# 注册视图函数
@home.route('/regist', methods=["GET", "POST"])
def regist():
    try:
        form = RegistForm()
        if request.method == "GET":
            return render_template("home/regist.html", regist_form=form)
        if form.validate_on_submit():
            name = form.name.data
            password = form.password1.data
            email = form.email.data
            if User.query.filter_by(name=name).first() is None:
                u = User(name=name, password=password, email=email)
                db.session.add(u)
                db.session.commit()
                flash("注册成功!")
                return redirect(url_for("home.login", code=0))
            else:
                flash("该用户名已被使用!")
        return render_template("home/regist.html", regist_form=form)

    except IntegrityError:
        flash("邮箱已被使用!")
        return render_template("home/regist.html", regist_form=form)


# 主页面
@home.route('/<int:page>')
@home.route('/page=<int:page>')
def mainpage(page):
    # 清空g容器中的数据
    global current_user
    current_user = ""
    # 连接数据库取数
    vs = Video.query.all()
    id_list = []
    title_list = []
    face_list = []
    goodnum_list = []
    danmaku_list = []
    # 数据列表list = data
    for v in vs:
        id_list.append(str(v.id))
        title_list.append(v.video_title)
        face_list.append(v.face)
        goodnum_list.append(v.Goodnum)
        danmaku_list.append(v.danmaku)
    total_num = len(vs)
    base_page = page
    if page > 1:
        page += 5
    start_page = page
    dest_page = page + 5
    if dest_page >= total_num:
        dest_page = total_num
    # 页数总数
    page_num = math.ceil(total_num / 6)
    return render_template('home/index.html',
                           start_page=start_page,
                           id_list=id_list,
                           title_list=title_list,
                           face_list=face_list,
                           goodnum_list=goodnum_list,
                           danmaku_list=danmaku_list,
                           dest_page=dest_page,
                           spage=base_page,
                           total_num=total_num,
                           page_num=page_num)


# 用户个人中心

@home.route('/usesr/<int:id>/<name>/<int:code>/page=<int:page>')
def user(id, name, code, page):
    is_admin = 0
    if Admin.query.filter_by(name=name).first() is not None:
        is_admin = 1
    secret_name = base64.b64encode(name.encode())
    print(secret_name)
    vs = Video.query.all()
    id_list = []
    title_list = []
    face_list = []
    goodnum_list = []
    danmaku_list = []
    # 数据列表list = data
    for v in vs:
        id_list.append(str(v.id))
        title_list.append(v.video_title)
        face_list.append(v.face)
        goodnum_list.append(v.Goodnum)
        danmaku_list.append(v.danmaku)
    total_num = len(vs)
    base_page = page
    if page > 1:
        page += 5
    start_page = page
    dest_page = page + 5
    if dest_page >= total_num:
        dest_page = total_num
    # 页数总数
    page_num = math.ceil(total_num / 6)
    # 连接redis数据库用g容器保存搜索记录以及条数
    global current_user_name
    current_user_name = name
    g.user = User.query.filter_by(name=name).first()
    g.username = name
    sr = StrictRedis()
    key_num = len(sr.lrange(name, 0, -1))  # 搜索记录条数
    new_list = [str(b, encoding="utf-8") for b in sr.lrange(name, 0, -1)]
    g.search_history = new_list
    g.key_num = key_num
    try:
        return render_template('home/user.html', userid=id, username=name, code=code,
                               spage=base_page, start_page=start_page, dest_page=dest_page, page_num=page_num,
                               id_list=id_list, title_list=title_list, face_list=face_list, goodnum_list=goodnum_list,
                               danmaku_list=danmaku_list, secret_name=secret_name, is_admin=is_admin,
                               new_list=g.search_history,
                               key_num=g.key_num)
    except AttributeError:
        return redirect(url_for('home.login', code=0))


@home.route('/user/<username>/userinfo', methods=["GET", "POST"])
def userinfo(username):
    form = Userinfo()
    u = User.query.filter_by(name=username).first()
    global hasface
    filename = username + '.jpg'
    file_error = 0
    if form.validate_on_submit():
        information = form.info.data
        f = form.face.data
        u.info = information
        # 接受发送来的表单数据
        if f:
            u.face = username + '.jpg'
            print(u.face)
            # 将发送来的头像文件保存至static目录下的faces文件夹中
            f.save(os.path.join(UPLOAD_FOLDER, filename))
        db.session.commit()
        flash("保存成功!")
        # 跳转到用户主页面
        return redirect(url_for("home.user", id=u.id, name=u.name, code=304, page=1))
    # 该变量保存该用户是否有自定义头像
    if os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
        hasface = 1
    # 上传格式错误
    if request.method != "GET":
        file_error = 1
    try:
        return render_template('home/userinfo-sub.html', username=username, email=u.email, info=u.info,
                               face=u.face,
                               form=form, hasface=hasface, userid=u.id, file_error=file_error,
                               new_list=g.search_history,
                               key_num=g.key_num)
    # 不经过登录直接访问时跳转到登录界面
    except AttributeError:
        return redirect(url_for('home.login', code=0))


# 修改密码页面
@home.route('/user/<username>/pwdchange', methods=["GET", "POST"])
def pwdchange(username):
    form = PwdForm()
    u = User.query.filter_by(name=username).first()
    if form.validate_on_submit():
        new_pwd = form.password1.data
        u.password = new_pwd
        db.session.commit()
        flash("修改成功!")
    try:
        return render_template('home/pwd.html', username=username, form=form, userid=u.id, new_list=g.search_history,
                               key_num=g.key_num)
    except AttributeError:
        return redirect(url_for("home.login", code=0))


# 收藏视频页面
@home.route('/user/<username>/favorite')
def favorite(username):
    movie_id_list = []
    id_list = []
    id = g.user.id
    face_list = []
    title_list = []
    goodnum_list = []
    danmaku_list = []
    secret_name = base64.b64encode(username.encode())
    if Favorite.query.filter_by(user_id=id).first() is None:
        movie_num = 0
    else:
        # 若用户收藏视频不为空，则获取收藏视频id并保存至movie_id_list中
        f_list = Favorite.query.filter_by(user_id=id).all()
        for f in f_list:
            movie_id = f.movie_id
            if str(movie_id) not in movie_id_list:
                movie_id_list.append(str(movie_id))
            else:
                continue
        id_list = sorted(movie_id_list)  # 收藏电影id列表(按id排列)
        movie_num = len(id_list)  # 收藏电影总数
        # 根据视频 id 获取视频相关信息
        for video_id in id_list:
            v = Video.query.filter_by(id=video_id).first()
            face_list.append(v.face)
            title_list.append(v.video_title)
            goodnum_list.append(v.Goodnum)
            danmaku_list.append(v.danmaku)
    try:
        return render_template('home/userfavorite.html', username=username, userid=id,
                               id_list=id_list, movie_num=movie_num, face_list=face_list, title_list=title_list,
                               goodnum_list=goodnum_list, danmaku_list=danmaku_list, secret_name=secret_name,
                               key_num=g.key_num,
                               new_list=g.search_history)
    except AttributeError:
        return redirect(url_for('home.login', code=0))


# 视频播放页面
@home.route('/<username>/play/<video_id>', methods=["POST", "GET"])
@home.route('/<username>/play/video_id=<video_id>', methods=["POST", "GET"])
def play(username, video_id):
    had_zan = 0  # 记录点赞
    had_fav = 0  # 记录收藏
    comment = 0
    content_list = []
    user_list = []
    time_list = []
    v = Video.query.filter_by(id=video_id).first()  # 定位视频对象
    form = CommentForm()
    cs = Comment.query.filter_by(movie_id=video_id).all()  # 定位评论对象
    show = 0
    if cs != None:  # 如果有评论
        comment = len(cs)
        content_list, user_list, time_list, face_list = get_comment(cs)  # 获取评论信息
        show = comment
    # 一页最多展示4条评论
    if comment > 4:
        show = 4
    url = 'movie_' + v.url  # 拼接视频url
    video_title = v.video_title
    info = v.info
    tag_id = v.tag_id
    tag_name = TAG_LIST[tag_id - 1]
    goodnum = v.Goodnum
    danmaku = v.danmaku
    for e in [".mp4", ".avi"]:
        new_url = url + e
        if os.path.exists(os.path.join(VIDEO_FOLDER, new_url)):
            break
    # 未登录状态访问视频界面
    if username == "not_login":
        return render_template("home/not_login_play.html", video_id=int(video_id), new_url=new_url,
                               video_title=video_title,
                               info=info, tag_name=tag_name, goodnum=goodnum, danmaku=danmaku, comment=comment,
                               time_list=time_list, user_list=user_list, face_list=face_list, content_list=content_list,
                               page_num=math.ceil(comment / 4), show=show
                               )

    username = base64.b64decode(username).decode()  # 用户名解码
    zan_video = Zan_records.query.filter_by(video_id=video_id).first()
    # u = User.query.filter_by(name=username).first()
    f = Fav_records.query.filter_by(video_id=video_id).first()
    fav_user_ids = f.fav_user_id  # 获取用户收藏记录
    zan_user_ids = zan_video.zan_user_id  # 获取用户点赞记录
    if str(g.user.id) in zan_user_ids.split('|'):
        had_zan = 1  # 点赞只能点赞一次
    if str(g.user.id) in fav_user_ids.split('|'):
        had_fav = 1  # 收藏只能收藏一次
    hav_comment = 0
    if form.validate_on_submit():  # 用户评论表单
        content = form.comment.data
        com = Comment(content=content, movie_id=video_id, user_id=g.user.id, add_time=datetime.date.today())
        db.session.add(com)
        db.session.commit()  # 将评论加到数据库中
        hav_comment = 1
        comment += 1
        show = comment
        cs = Comment.query.filter_by(movie_id=video_id).all()
        content_list, user_list, time_list, face_list = get_comment(cs)  # 更新信息列表
    # 添加评论过后重新判断展示条数
    if comment > 4:
        show = 4
    try:
        return render_template("home/login_play.html", userid=g.user.id, new_url=new_url, video_title=video_title,
                               info=info, tag_name=tag_name, goodnum=goodnum, danmaku=danmaku, username=username,
                               video_id=int(video_id), had_zan=had_zan, had_fav=had_fav, content_list=content_list,
                               comment=comment, time_list=time_list, user_list=user_list, face_list=face_list,
                               page_num=math.ceil(comment / 4),
                               show=show, hav_comment=hav_comment, user_face=g.user.face, form=form,
                               new_list=g.search_history,
                               key_num=g.key_num)
    except AttributeError:
        return redirect(url_for('home.login', code=video_id))


# 该视图函数用于处理用户点赞时发送的ajax请求
@home.route('/zan_handler/<username>', methods=["GET", "POST"])
def zan_handler(username):
    # 获取ajax请求中的数据
    data = request.get_json("data")
    pointer = data["pointer"]
    video_id = data["video_id"]
    user_id = g.user.id
    v = Video.query.filter_by(id=video_id).first()
    # 获取该视频被哪些用户点过赞
    des_video = Zan_records.query.filter_by(video_id=video_id).first()
    goodnum = v.Goodnum
    add_string = "|" + str(user_id)
    if pointer == "add":
        # 添加点赞记录,点赞数加一
        des_video.zan_user_id += add_string
        v.Goodnum = goodnum + 1
    else:
        des_video.zan_user_id = des_video.zan_user_id.replace(add_string, "")
        v.Goodnum = goodnum - 1
    db.session.commit()
    return str(v.Goodnum)


# 该函数用户处理点击收藏时发送来的ajax请求
@home.route('/favorite_hanlder/<username>', methods=["POST", "GET"])
def favorite_handler(username):
    data = request.get_json("data")
    pointer = data["pointer"]
    video_id = data["video_id"]
    user_id = g.user.id
    fav_obj = Fav_records.query.filter_by(video_id=video_id).first()
    add_string = "|" + str(user_id)
    if pointer == "add_fav":  # 加入收藏
        fav_obj.fav_user_id += add_string
        f_add = Favorite(movie_id=video_id, user_id=user_id)
        db.session.add(f_add)

    else:  # 取消收藏
        fav_obj.fav_user_id = fav_obj.fav_user_id.replace(add_string, "")
        f_del = Favorite.query.filter(and_(Favorite.movie_id == video_id, Favorite.user_id == user_id)).first()
        db.session.delete(f_del)
    db.session.commit()
    return username


# 该函数用于处理用户点击评论列表上一页或下一页的情况
@home.route("/comment_handler/<int:video_id>", methods=["POST", "GET"])
def comment_handler(video_id):
    data = request.get_json("data")
    comment_num = data["comment_num"]
    page = data["page"]
    page_num = math.ceil(comment_num / 4)
    html = ""
    cs = Comment.query.filter_by(movie_id=video_id).all()  # 获取评论列表

    if page * 4 <= comment_num:  # 显示4条评论的情况
        start = (page - 1) * 4
        end = (page - 1) * 4 + 4
    else:  # 最后一页，且显示评论少于四条
        start = (page_num - 1) * 4
        end = start + comment_num % 4
    for c in cs[start:end]:
        user_id = c.user_id
        u = User.query.filter_by(id=user_id).first()
        un = u.name
        if u.face == "None":
            html += '<div class="common-item"><div class="user-face" style="height:100px;width:100px;float:left;"><img class="face" src="/static/faces/default.jpg" width="50px" height="50px"></div><div style="height:100px;width:500px;float:left;word-wrap:break-word"><p style="font-size:25px;color:red;">' + un + \
                    '</p><p class="comment-content">' + c.content + \
                    '</p><p class="comment-time" style="font-size:12px;position:relative;left:350px;">发布于' + change_time_form(
                c.add_time) + '</p></div></div><hr>'
        else:
            html += r'<div class="common-item"><div class="user-face" style="height:100px;width:100px;float:left;"><img class="face" src="/static/faces/' + u.name + '.jpg"' + ' width="50px" height="50px"></div><div style="height:100px;width:500px;float:left;word-wrap:break-word"><p style="font-size:25px;color:red;">' + un + \
                    '</p><p class="comment-content">' + c.content + \
                    '</p><p class="comment-time" style="font-size:12px;position:relative;left:350px;">发布于' + change_time_form(
                c.add_time) + '</p></div></div><hr>'
    return html


# 视频投稿
@home.route('/<username>/<int:id>/create', methods=["GET", "POST"])
def create(username, id):
    form = CreateForm()
    if form.validate_on_submit():
        video_title = form.video_title.data
        info = form.info.data
        face = form.face.data
        tag = form.tag.data
        tag_id = TAG_LIST.index(tag) + 1
        video = form.video_file.data
        v_num = video.query.all()
        id_list = [v.id for v in v_num]
        new_id = numpy.max(id_list) + 1  # 新加入的视频的id
        face_name = "None"
        # 用户有上传视频封面的情况
        if face is not None:
            new_face_url = str(new_id) + ".jpg"
            # 将视频封面保存下来
            face.save(os.path.join(VIDEO_FACE_FOLDER, new_face_url))
            face_name = new_face_url
        if video:
            new_video_url = "movie_" + str(new_id) + ".mp4"
            video.save(os.path.join(VIDEO_FOLDER, new_video_url))
        # 添加视频记录，点赞记录，收藏记录
        add_v = Video(video_title=video_title, url=str(new_id), info=info, face=face_name, tag_id=tag_id,
                      Goodnum=0, danmaku=0)
        add_fav = Fav_records(id=new_id, video_id=new_id, fav_user_id="")
        add_zan = Zan_records(id=new_id, video_id=new_id, zan_user_id="")
        db.session.add(add_v)
        db.session.commit()
        db.session.add(add_fav)
        db.session.commit()
        db.session.add(add_zan)
        db.session.commit()
        return redirect(url_for("home.user", id=id, name=username, code=99, page=1))
    try:
        return render_template("home/create.html", userid=id, username=username, form=form, key_num=g.key_num,
                               new_list=g.search_history)
    except AttributeError:
        return redirect(url_for('home.login', code=0))


# 分类页面
@home.route('/<username>/tag=<int:tag_id>/show')
def tag_show(username, tag_id):
    is_admin = 0
    if Admin.query.filter_by(name=username).first() is not None:
        is_admin = 1
    video = Tag.query.filter_by(id=tag_id).first()
    vs = [v.id for v in video.videoes]
    face_list = [v.face for v in video.videoes]
    title_list = [v.video_title for v in video.videoes]
    goodnum_list = [v.Goodnum for v in video.videoes]
    danmaku_list = [v.danmaku for v in video.videoes]
    video_num = len(vs)
    tag_name = TAG_LIST[tag_id - 1]
    if username == "not_login":
        return render_template("home/nolog_tag_show.html", tag_id=tag_id, video=vs, video_num=video_num,
                               tag_name=tag_name,
                               face_list=face_list, title_list=title_list, goodnum_list=goodnum_list,
                               danmaku_list=danmaku_list)
    userid = User.query.filter_by(name=username).first().id
    secret_name = base64.b64encode(username.encode())
    try:
        return render_template("home/tag_show.html", username=username, tag_id=tag_id, video=vs, video_num=video_num,
                               userid=userid,
                               tag_name=tag_name, secret_name=secret_name, face_list=face_list, title_list=title_list,
                               goodnum_list=goodnum_list, new_list=g.search_history, key_num=g.key_num,
                               danmaku_list=danmaku_list, is_admin=is_admin)
    except AttributeError:
        return redirect(url_for('home.login', code=0))


# 该函数用于处理点击搜索时发送的ajax请求
@home.route('/search_handler/<username>', methods=["POST", "GET"])
def search_handler(username):
    data = request.get_json("data")
    key = data["key"]
    new_url = url_for("home.search", key=key, username=username)
    return new_url


@home.route('/search/<username>/kw=<key>')
def search(key, username):
    vs = Video.query.all()
    result_ids = [v.id for v in vs if key in v.video_title]
    result_faces = [v.face for v in vs if key in v.video_title]
    result_titles = [v.video_title for v in vs if key in v.video_title]
    result_goodnums = [v.Goodnum for v in vs if key in v.video_title]
    result_danmaku = [v.danmaku for v in vs if key in v.video_title]
    v_num = len(result_ids)
    if username == "not_login":
        return render_template("home/not_login_search.html", key=key, video_num=v_num, id_list=result_ids,
                               face_list=result_faces, title_list=result_titles, goodnum_list=result_goodnums,
                               danmaku_list=result_danmaku)
    sr = StrictRedis()  # 连接redis
    whole_list = [str(b, encoding="utf-8") for b in sr.lrange(username, 0, -1)]  # 获取搜索记录
    if key in whole_list:
        sr.lrem(username, -1, bytes(key, encoding="utf-8"))  # 若记录中存在该关键字，则将关键字提前
    sr.lpush(username, key)  # 将搜索关键字加入list中，list名为用户名
    key_num = len(sr.lrange(username, 0, -1))  # 搜索记录条数
    if key_num > 5:
        sr.rpop(username)  # 从右边删除多的记录,搜索记录最多五条
        key_num = 5
    new_list = [str(b, encoding="utf-8") for b in sr.lrange(username, 0, -1)]
    # 更新g中的变量
    try:
        g.search_history = new_list
        g.key_num = key_num
        userid = g.user.id
        secret_name = base64.b64encode(username.encode())
        return render_template("home/search.html", key=key, video_num=v_num, id_list=result_ids,
                               face_list=result_faces, title_list=result_titles, goodnum_list=result_goodnums,
                               danmaku_list=result_danmaku, username=username, userid=userid, secret_name=secret_name,
                               new_list=new_list, key_num=key_num)
    except AttributeError:
        return redirect(url_for('home.login', code=0))


@home.route('/rank/<username>')
def rank(username):
    vs = Video.query.order_by(Video.Goodnum.desc()).all()
    result_faces = [v.face for v in vs]
    result_titles = [v.video_title for v in vs]
    result_goodnums = [v.Goodnum for v in vs]
    result_danmaku = [v.danmaku for v in vs]
    if username == "not_login":
        return render_template("home/nolog_rank.html", face_list=result_faces, title_list=result_titles,
                               goodnum_list=result_goodnums,
                               danmaku_list=result_danmaku, video_num=len(vs))
    userid = g.user.id
    secret_name = base64.b64encode(username.encode())
    return render_template("home/rank.html", username=username, userid=userid, secret_name=secret_name,
                           face_list=result_faces, title_list=result_titles, goodnum_list=result_goodnums,
                           danmaku_list=result_danmaku, video_num=len(vs), key_num=g.key_num, new_list=g.search_history)


@home.errorhandler(404)
def handler():
    return "404"

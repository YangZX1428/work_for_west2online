from . import admin
from .forms import adminForm
from ..models import User, Video, Admin, Comment, Zan_records, Fav_records, db, Favorite, Adminlog, Oplog, Tag, Userlog
from flask import render_template, redirect, url_for, request, flash
import base64
import math
import time
import datetime
import os
from ..home.views import TAG_LIST, VIDEO_FOLDER, VIDEO_FACE_FOLDER
from redis import StrictRedis


def change_time_form(mtime):
    ul_time = time.mktime(mtime.timetuple())
    return str(datetime.datetime.fromtimestamp(ul_time))[0:10]


def change_time_form_2(mtime):
    ul_time = time.mktime(mtime.timetuple())
    return str(datetime.datetime.fromtimestamp(ul_time))


def get_comment(cs):
    content_list = []  # 评论内容列表
    user_list = []  # 评论用户列表
    time_list = []  # 评论时间列表
    face_list = []
    id_list = []
    for c in cs:
        content_list.append(c.content)
        u = User.query.filter_by(id=c.user_id).first()
        user_list.append(u.name)
        time_list.append(change_time_form(c.add_time))
        face_list.append(u.face)
        id_list.append(c.id)
    return content_list, user_list, time_list, face_list, id_list


@admin.route('/mainpage/<username>/page=<int:page>/<int:code>')
def mainpage(username, page, code):
    userid = User.query.filter_by(name=username).first().id
    secret_name = base64.b64encode(username.encode())
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
    sr = StrictRedis()
    name = "admin_"+username
    key_num = len(sr.lrange(name, 0, -1))  # 搜索记录条数
    new_list = [str(b, encoding="utf-8") for b in sr.lrange(name, 0, -1)]
    print(key_num)
    return render_template('admin/mainpage.html', userid=userid, username=username,
                           spage=base_page, start_page=start_page, dest_page=dest_page, page_num=page_num,
                           id_list=id_list, title_list=title_list, face_list=face_list, goodnum_list=goodnum_list,
                           danmaku_list=danmaku_list, secret_name=secret_name, code=code, total_num=total_num,
                           new_list=new_list, key_num=key_num)


@admin.route('/login', methods=["POST", "GET"])
def login():
    form = adminForm()
    if form.validate_on_submit():
        username = form.account.data
        pw = form.password.data
        a = Admin.query.filter_by(name=username).first()
        if a != None:
            if a.pwd == pw:
                return redirect(url_for('admin.mainpage', username=username, page=1, code=200))
            else:
                flash("密码错误!")
        else:
            flash("账号不存在!")
    return render_template("admin/login.html", form=form)


# 视频管理界面
@admin.route('/play/<username>/video_id=<int:video_id>')
def play(username, video_id):
    comment = 0
    content_list = []
    user_list = []
    time_list = []
    face_list = []
    id_list = []
    v = Video.query.filter_by(id=video_id).first()  # 定位视频对象
    cs = Comment.query.filter_by(movie_id=video_id).all()  # 定位评论对象
    show = 0
    if cs != None:  # 如果有评论
        comment = len(cs)
        content_list, user_list, time_list, face_list, id_list = get_comment(cs)  # 获取评论信息
        show = comment
    if comment > 4:
        show = 4
    url = 'movie_' + v.url  # 拼接视频url
    video_title = v.video_title
    info = v.info
    tag_id = v.tag_id
    tag_name = TAG_LIST[tag_id - 1]
    goodnum = v.Goodnum
    danmaku = v.danmaku
    userid = User.query.filter_by(name=username).first().id
    for e in [".mp4", ".avi"]:
        new_url = url + e
        if os.path.exists(os.path.join(VIDEO_FOLDER, new_url)):
            break
    sr = StrictRedis()
    name = "admin_" + username
    key_num = len(sr.lrange(name, 0, -1))  # 搜索记录条数
    new_list = [str(b, encoding="utf-8") for b in sr.lrange(name, 0, -1)]
    return render_template("admin/play.html", userid=userid, new_url=new_url, video_title=video_title,
                           info=info, tag_name=tag_name, goodnum=goodnum, danmaku=danmaku, username=username,
                           video_id=int(video_id), content_list=content_list,new_list = new_list,key_num = key_num,
                           comment=comment, time_list=time_list, user_list=user_list, face_list=face_list,
                           page_num=math.ceil(comment / 4),
                           show=show, id_list=id_list)


@admin.route("/comment_handler/<int:video_id>", methods=["POST", "GET"])
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
                    '</p><p class="comment-time" style="font-size:12px;position:relative;left:350px;">发布于' \
                    + change_time_form(c.add_time) + '</p><a id="del-' + str(
                c.id) + '" class="delete-comment" href="javascript:void(0)" onclick="Delc(this)">删除该评论</a></div></div><hr>'
        else:
            html += r'<div class="common-item"><div class="user-face" style="height:100px;width:100px;float:left;"><img class="face" src="/static/faces/' + u.name + '.jpg"' + ' width="50px" height="50px"></div><div style="height:100px;width:500px;float:left;word-wrap:break-word"><p style="font-size:25px;color:red;">' + un + \
                    '</p><p class="comment-content">' + c.content + \
                    '</p><p class="comment-time" style="font-size:12px;position:relative;left:350px;">发布于' + \
                    change_time_form(c.add_time) + '</p><a id="del-' + str(
                c.id) + '" class="delete-comment" href="javascript:void(0)" onclick="Delc(this)">删除该评论</a></div></div><hr>'
    return html


@admin.route('/delete_handler', methods=["POST", "GET"])
def delete_handler():
    data = request.get_json("data")
    admin_username = data["admin_name"]
    video_id = data["video_id"]
    cs = Comment.query.filter_by(movie_id=video_id).all()  # 删除相关评论记录
    z_rs = Zan_records.query.filter_by(video_id=video_id).first()  # 删除相关点赞记录
    f_rs = Fav_records.query.filter_by(video_id=video_id).first()  # 删除相关收藏记录
    vs = Video.query.filter_by(id=video_id).first()  # 删除相关视频信息
    fav = Favorite.query.filter_by(movie_id=video_id).first()  # 删除对应收藏
    face = vs.face
    u = "movie_" + vs.url + ".mp4"
    for c in cs:
        db.session.delete(c)
        db.session.commit()
    db.session.delete(z_rs)
    db.session.commit()
    db.session.delete(f_rs)
    db.session.commit()
    db.session.delete(vs)
    db.session.commit()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    if face is not "None":
        os.remove(os.path.join(VIDEO_FACE_FOLDER, face))  # 删除对应视频封面
    if u:
        os.remove(os.path.join(VIDEO_FOLDER, u))  # 删除对应视频文件
    # 添加操作日志
    admin_id = Admin.query.filter_by(name=admin_username).first().id
    content = "删除了编号为" + str(video_id) + "的视频"
    admin_log = Oplog(admin_id=admin_id, option_content=content)
    db.session.add(admin_log)
    db.session.commit()

    url = url_for("admin.mainpage", username=admin_username, page=1, code=300)
    return url


@admin.route('/<username>/tag=<int:tag_id>/show')
def tag_show(username, tag_id):
    video = Tag.query.filter_by(id=tag_id).first()
    vs = [v.id for v in video.videoes]
    face_list = [v.face for v in video.videoes]
    title_list = [v.video_title for v in video.videoes]
    goodnum_list = [v.Goodnum for v in video.videoes]
    danmaku_list = [v.danmaku for v in video.videoes]
    video_num = len(vs)
    tag_name = TAG_LIST[tag_id - 1]
    userid = User.query.filter_by(name=username).first().id
    sr = StrictRedis()
    name = "admin_" + username
    key_num = len(sr.lrange(name, 0, -1))  # 搜索记录条数
    new_list = [str(b, encoding="utf-8") for b in sr.lrange(name, 0, -1)]
    return render_template("admin/tag_show.html", username=username, tag_id=tag_id, video=vs, video_num=video_num,
                           userid=userid,key_num = key_num,new_list = new_list,
                           tag_name=tag_name, face_list=face_list, title_list=title_list, goodnum_list=goodnum_list,
                           danmaku_list=danmaku_list)


@admin.route('/search_handler/<username>', methods=["POST", "GET"])
def search_handler(username):
    print(username)
    data = request.get_json("data")
    key = data["key"]
    new_url = url_for("admin.search", key=key, username=username)
    return new_url


@admin.route('/search/<username>/kw=<key>')
def search(key, username):
    print(username)
    vs = Video.query.all()
    result_ids = [v.id for v in vs if key in v.video_title]
    result_faces = [v.face for v in vs if key in v.video_title]
    result_titles = [v.video_title for v in vs if key in v.video_title]
    result_goodnums = [v.Goodnum for v in vs if key in v.video_title]
    result_danmaku = [v.danmaku for v in vs if key in v.video_title]
    v_num = len(result_ids)
    sr = StrictRedis()  # 连接redis
    name = "admin_"+username
    whole_list = [str(b, encoding="utf-8") for b in sr.lrange(name, 0, -1)]  # 获取搜索记录
    if key in whole_list:
        sr.lrem(name, -1, bytes(key, encoding="utf-8"))  # 若记录中存在该关键字，则将关键字提前
    sr.lpush(name, key)  # 将搜索关键字加入list中，list名为用户名
    key_num = len(sr.lrange("admin_"+username, 0, -1))  # 搜索记录条数
    if key_num > 5:
        sr.rpop(name)  # 从右边删除多的记录,搜索记录最多五条
        key_num = 5
    new_list = [str(b, encoding="utf-8") for b in sr.lrange(name, 0, -1)]
    userid = User.query.filter_by(name=username).first().id
    print(key_num)
    return render_template("admin/search.html", key=key, video_num=v_num, id_list=result_ids,
                           face_list=result_faces, title_list=result_titles, goodnum_list=result_goodnums,
                           danmaku_list=result_danmaku, username=username, userid=userid, new_list=new_list,
                           key_num=key_num)


@admin.route('/delete_comment_handler', methods=["POST", "GET"])
def delete_comment_handler():
    data = request.get_json("data")
    comment_id = data["comment_id"]
    username = data["username"]
    video_id = data["video_id"]
    comment_id = int(comment_id[4:])
    # 删除评论记录
    c = Comment.query.filter_by(id=comment_id).first()
    content = c.content
    db.session.delete(c)
    db.session.commit()
    if len(content) > 20:
        op = '删除了评论 "' + content[0:20] + '"...'
    else:
        op = '删除了评论 "' + content + '"'
    admin_id = Admin.query.filter_by(name=username).first().id
    oplog = Oplog(admin_id=admin_id, option_content=op)
    db.session.add(oplog)
    db.session.commit()
    return url_for('admin.play', username=username, video_id=video_id)


@admin.route('/<username>/login_log')
def login_log(username):
    log = Userlog.query.all()
    username_list = []
    user_id = [l.user_id for l in log]
    add_time = [change_time_form_2(l.time) for l in log]
    for id in user_id:
        username_list.append(User.query.filter_by(id=id).first().name)
    return render_template("admin/login_log.html", username_list=username_list, add_time=add_time, username=username,
                           log_num=len(log))


@admin.route('/<username>/op_log')
def op_log(username):
    log = Oplog.query.all()
    admin_id_list = [l.admin_id for l in log]
    add_time = [change_time_form_2(l.add_time) for l in log]
    content = [l.option_content for l in log]
    admin_name = []
    for id in admin_id_list:
        admin_name.append(Admin.query.filter_by(id=id).first().name)
    log_num = len(log)
    return render_template("admin/op_log.html", admin_name=admin_name, add_time=add_time, content=content,
                           log_num=log_num,
                           username=username)

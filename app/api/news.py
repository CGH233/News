#coding:utf-8

import json
import time
from . import api
from app import db
from app.models import User, News, Comments
from flask import jsonify, request, Response

@api.route('/news/list/<int:page>/', methods = ['GET'])
def news_list(page):
    all_news = News.query.all()
    dataList = []
    news_num = 0
    page_news_limit = 10
    if not all_news:
        return jsonify({"msg":"no news now"}), 403
    for news in all_news[::-1]:
        news_num += 1
        if news_num > (page-1)*page_news_limit and news_num <= page*page_news_limit:
            newsList = {} 
            newsList['news_id'] = news.id
            newsList['title'] = news.title
            newsList['content'] = (news.content)[:51]
            newsList['photo'] = news.photo
            newsList['time'] = news.time
            newsList['commentsnum'] = Comments.query.filter_by(news_id=news.id).count()
            dataList.append(newsList)
        elif news_num > page*page_news_limit:
            break
    return jsonify({"newslist":dataList}),200


@api.route('/news/<int:news_id>/', methods = ['GET'])
def news_information(news_id):
    if request.method == 'GET':
        news = News.query.filter_by(id=news_id).first()
        if news is  None:
            return jsonify({"msg":"news is not exist"}),403
        title = news.title
        content = news.content
        photo = news.photo
        time = news.time
        comments_list = []
        comments = Comments.query.filter_by(news_id=news_id).all()
        for comment in comments:
            data = {}
            data['comment_id'] = comment.id
            data['username'] = User.query.filter_by(id=comment.user_id).first().username
            data['time'] = comment.time
            data['content'] = comment.content
            comments_list.append(data)
        return jsonify({"title":title,
                        "content":content,
                        "photo":photo,
                        "time":time
                        "comments_list":comments_list,}),200


@api.route('/news/', methods = ['POST'])
@User.token_check(1)
def write_news(user_id):
    if request.method == 'POST':
        title = request.get_json().get('title')
        content = request.get_json().get('content')
        photo = request.get_json().get('photo')
        time =  time.strftime("%Y-%m-%d %a %H:%M", time.localtime())
        news = News(title = title,
                    content = content,
                    photo = photo,
                    time = time,)
        db.session.add(news)
        db.session.commit()
        return jsonify({"msg":"add news successful!"}),200


@api.route('/news/<int:news_id>/', methods = ['DELETE'])
@User.token_check(1)
def delete_news(user_id, news_id):
    if request.method == 'DELETE':
        news = News.query.filter_by(id=news_id).first()
        if news:
            News.query.filter_by(id=news_id).delete()
            return jsonify({"msg":"news has been deleted!"}),200
        else:
            return jsonify({"msg":"news is not exist"}),403



@api.route('/news/<int:news_id>/comment/', methods = ['POST'])
@User.token_check(0)
def write_comment(user_id, news_id):
    if request.method == 'POST':
        if News.query.filter_by(id=news_id).first():
            content = request.get_json().get('content')
            time =  time.strftime("%Y-%m-%d %a %H:%M", time.localtime())
            comment = Comments(content = content,
                               time = time,
                               user_id = user_id,
                               news_id = news_id,)
            db.session.add(comment)
            db.session.commit()
            return jsonify({"msg":"cooment add successful!"}),200
        else:
            return jsonify({"msg":"news is not exist!"}),403


@api.route('/comment/<int:comment_id>/', methods = ['DELETE'])
@User.token_check(0)
def delete_comment(user_id, comment_id):
    if request.method == 'DELETE':
        comment = Comments.query.filter_by(id=comment_id).first()
        if comment:
            if user_id == comment.user_id:
                Comments.query.filter_by(id=comment_id).delete()
                return jsonify({"msg":"comment has been delete!"}),200
            else:
                return jsonify({"msg":"you are not allowed to  do that!"}),403
        else:
            return jsonify({"msg":"comment is not exist"}),403

        

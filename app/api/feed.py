#coding:utf-8
import json
import time
from . import api
from app import db
from app.models import Feed, User
from flask import jsonify, request, Response

@api.route('/feed/', methods = ['POST'])
@User.token_check(0)
def new_feed(user_id):
    if request.method == 'POST':
        content = request.get_json().get('content')
        localtime = time.strftime("%Y-%m-%d %a %H:%M", time.localtime())
        feed = Feed(content = content,
                    time = localtime, 
                    user_id = user_id)
        db.session.add(feed)
        db.session.commit()
        return jsonify({"msg":"feed add successful!"}),200



@api.route('/feed/<int:feed_id>/', methods = ['DELETE'])
@User.token_check(0)
def delete_feed(user_id, feed_id):
    if request.method == 'DELETE':
        feed = Feed.query.filter_by(id=feed_id).first()
        if feed:
            if feed.user_id == user_id:
                Feed.query.filter_by(id=feed_id).delete()
                return jsonify({"msg":"feed has been delete!"}),200
            else:
                return jsonify({"msg":"wrong user!"}),403
        else:
            return jsonify({"msg":"feed is not exist"}),403


@api.route('/feed/list/<int:page>/', methods = ['GET'])
def feed_list(page):
    if request.method == 'GET':
        feed_list = Feed.query.all()
        feed_num = 0
        feedList = []
        page_feed_limit = 10
        for feed in feed_list:
            feed_num += 1
            if feed_num > (page-1)*page_feed_limit and feed_num <= page*page_feed_limit:
                a_feed = {}
                a_feed['content'] = feed.content
                a_feed['feed_id'] = feed.id
                a_feed['username'] = User.query.filter_by(id=feed.user_id).first().username
                a_feed['time'] = feed.time
                feedList.append(a_feed)
            elif feed_num > page*page_feed_limit:
                break
        return jsonify({"feedlist":feedList}),200

#coding: utf-8
from . import api
from app import db
from flask import request, jsonify, Response
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User
import json

@api.route('/signup/', methods = ['POST'])
def signup():
    if request.method == 'POST':
        account = request.get_json().get("account")
        username = request.get_json().get('username')
        password = request.get_json().get('password')
        if not User.query.filter_by(account=account).first():
            user = User(account = account,
                        username = username,
                        password = password,
                        role = 0)
            db.session.add(user)
            db.session.commit()
            return jsonify({
                "message":"ok"
            }),200
        else:
            return jsonify({
                "message":"user is existed"
            }),400

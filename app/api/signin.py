#coding:utf-8
from . import api
from app import db
from flask import request,jsonify,Response
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User
import json

@api.route('/signin/', methods = ['POST'])
def signin():
    if request.method == 'POST':
        username = request.get_json().get("username")
        password = request.get_json().get("password")
        try:
            user = User.query.filter_by(username = username).first()
        except:
            user = None
            return jsonify({"msg":"wrong username"}),400
        if user is not None and user.verify_password(password):
            uid = user.id
            token = user.generate_confirmation_token()
            return jsonify({
                "uid":user.id,
                "token":token,
            }),200
        else:
            return jsonify({
                "msg":"wrong password"
            }),401

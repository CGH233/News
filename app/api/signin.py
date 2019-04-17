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
        account = request.get_json().get("account")
        password = request.get_json().get("password")
        try:
            user = User.query.filter_by(account=account).first()
        except:
            user = None
            return jsonify({"msg":"wrong account"}),400
        if user is not None and user.verify_password(password):
            username = user.username
            token = user.generate_confirmation_token()
            return jsonify({
                "token":token,
                "username":username,
            }),200
        else:
            return jsonify({
                "msg":"wrong password"
            }),401

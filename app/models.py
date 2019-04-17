# coding :utf-8
from flask import current_app, request, url_for, jsonify
from flask_login import UserMixin, AnonymousUserMixin, current_user
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from functools import wraps
import json

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Integer)
    comments = db.relationship('Comments', backref='users', lazy='dynamic')
    feed = db.relationship('Feed', backref='users', lazy='dynamic')
    confirmed = db.Column(db.Boolean, defaulti=False)
    
    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600000000000):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')
        
    def token_check(role_needed):    
        def confirm(f):
            @wraps(f)
            def decorated_func(*args, **kwargs):
                if request.headers['token'] is None:
                    return jsonify({"msg":"you should siginin first!"}), 401
                s = Serializer(current_app.config['SECRET_KEY'])
                try:
                    data = s.loads(request.headers['token'].encode('utf-8'))
                except:
                    return jsonify({"msg":"wrong token"}), 401
                user_id = data.get('confirm')
                role = User.query.filter_by(id=user_id).first().role
                if role_needed > role:
                    return jsonify({"msg":"you can't do this"}),401
                rv = f(user_id, *args, **kwargs)
                return rv
            return decorated_func
        return confirm

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, index=True)
    content = db.Column(db.Text)
    photo = db.Column(db.String(50))
    time = db. Column(db.String(30))
    comments = db.relationship('Comments', backref='news', passive_deletes=True, cascade='delete', lazy='dynamic')

class Comments(db.Model):
    __tablename__ = 'commments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    time = db.Column(db.String(64))
    news_id = db.Column(db.Integer, db.ForeignKey(('news.id'), ondelete='cascade'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Feed(db.Model):
    __tablename__ = 'feed'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    time = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

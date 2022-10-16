from os import access
from src.constants.http_status_codes import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from src.database import User, db
import validators
from flask_jwt_extended import create_access_token, create_refresh_token

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post('/register')
def register():
    
    if not request.json:
        return jsonify({'error': "Missing information"}), HTTP_400_BAD_REQUEST

    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if len(password) < 6:
        return jsonify({'error': "Passwords is too short"}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({'error': "Username is too short"}), HTTP_400_BAD_REQUEST
    
    if not username.isalnum() or " " in username:
        return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST
    
    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': "Username is taken"}), HTTP_409_CONFLICT
    
    pwd_hash=generate_password_hash(password)
    user = User(username=username, password=pwd_hash, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': "User created",
        'user':{
            'username': username, 'email': email
            }
        }), HTTP_201_CREATED

@auth.post('/login')
def login():

    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password, password)
        
        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return jsonify({
                'user':{
                    'refresh': refresh,
                    'access': access,
                    'username': user.username,
                    'email': user.email
                }
            })

    return jsonify({'error': "Wrong credentials"}), HTTP_401_UNAUTHORIZED
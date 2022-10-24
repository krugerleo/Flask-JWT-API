from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, jsonify, request
from src.database import Bookmark, db
from flask_jwt_extended import current_user, jwt_required, get_jwt_identity
import validators 

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")

@bookmarks.post('/')
@jwt_required()
def post_bookmark():
    current_user = get_jwt_identity()
    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({
            'error': 'Enter a valid url'
        }), HTTP_400_BAD_REQUEST

    if Bookmark.query.filter_by(url=url).first():
        return jsonify({
            'error': 'URL already exists'
        }), HTTP_409_CONFLICT

    bookmark = Bookmark(url=url, body=body, user_id=current_user)
    db.session.add(bookmark)
    db.session.commit()
    
    return jsonify({
        'ID':bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at
    }), HTTP_201_CREATED

@bookmarks.get('/')
@jwt_required()
def get_bookmarks():
    current_user = get_jwt_identity()
    bookmarks = Bookmark.query.filter_by(user_id = current_user)

    data = []

    for bookmark in bookmarks:
        data.append({
            'ID':bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        })
    
    return jsonify({'data':data}),HTTP_200_OK

@bookmarks.get('/<int:id>')
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({
            'message':'Item not found'
        }), HTTP_404_NOT_FOUND

    return jsonify({
        'ID':bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at
    }), HTTP_200_OK
from flask import Blueprint, json, request, redirect, url_for
from flask_jwt_extended import jwt_required
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.friendships import Friendships, FriendshipSchema
from api.utils.database import db
from sqlalchemy import or_, tuple_

friendship_routes = Blueprint('friendship_routes', __name__)

@friendship_routes.route('/send/friend/request', methods=['post'])
@jwt_required
def send_friend_request():
    data = request.get_json()
    data['status'] = 0
    if (data['user_one'] is not data['user_two']):
        if (Friendships.find_if_request_exists(data['user_one'], data['user_two']) is None and
        Friendships.find_if_request_exists_reverse(data['user_one'], data['user_two']) is None):
            fr_schema = FriendshipSchema()
            friendship = fr_schema.load(data)
            result = fr_schema.dump(friendship.create())
            return redirect(url_for('user_routes.find_friend_requester', user_id=data['user_one']))
        else:
            return response_with(resp.BAD_REQUEST_400)
    else:
        return response_with(resp.BAD_REQUEST_400)

@friendship_routes.route('/get/friend/requests/<int:user_id>', methods=['get'])
@jwt_required
def get_friend_request(user_id):
    fetched = Friendships.query.filter_by(user_two=user_id, status=0).all()
    friend_schema = FriendshipSchema(many=True, only=['user_one'])
    friends = friend_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={'friend_requests': friends})

@friendship_routes.route('/delete/request/<int:user_id>/<int:other_id>', methods=['delete'])
@jwt_required
def delete_request(user_id, other_id):
    fetched = Friendships.query.filter_by(user_one=other_id, user_two=user_id).first()
    db.session.delete(fetched)
    db.session.commit()
    return response_with(resp.SUCCESS_200)

@friendship_routes.route('/accept/friend/request/<int:user_id>/<int:other_id>', methods=['post'])
def update_friendship_status(user_id, other_id):
    fetched = Friendships.query.filter_by(user_one=other_id, user_two=user_id).first()
    fetched.status = 1
    fetched.action_user = int(user_id)
    db.session.add(fetched)
    db.session.commit()
    return response_with(resp.SUCCESS_200)

@friendship_routes.route('/friends/chat/list/<int:user_id>', methods=['get'])
@jwt_required
def user_friends_chat_list(user_id):
    fetched = Friendships.query.filter(or_(Friendships.user_one.like(user_id), Friendships.user_two.like(user_id)))
    friend_schema = FriendshipSchema(many=True)
    friends = friend_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={'friends': friends})
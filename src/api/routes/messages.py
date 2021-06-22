from flask import Blueprint, json, request, redirect, url_for
from flask_jwt_extended import jwt_required
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.messages import MessageSchema, Messages
import random, string

message_routes = Blueprint('message_routes', __name__)

@message_routes.route('/create/room/<int:sender_id>/<int:receiver_id>', methods=['get'])
def create_chat_room(sender_id, receiver_id, room_name):
    data = {
        'room_name': '',
        'sender_id': 0,
        'receiver_id': 0,
        'message': ''
    }
    message='Sent Request'
    data['room_name'] = room_name
    data['sender_id'] = sender_id
    data['receiver_id'] = receiver_id
    data['message'] = message
    msg_schema = MessageSchema()
    msg = msg_schema.load(data)
    result = msg_schema.dump(msg.create())
    return response_with(resp.SUCCESS_200, value={'message' : result})

@message_routes.route('/get/chat/room/<int:user_id>/<int:other_id>', methods = ['get'])
@jwt_required
def get_message_list(user_id, other_id):
    first = Messages.find_by_user_one(user_id, other_id)
    second = Messages.find_by_user_two(user_id, other_id)
    if (first is not None):
        fetched = Messages.query.filter_by(room_name=first.room_name).all()
        msg_schema = MessageSchema(many=True, only=['message', 'sender_id', 'receiver_id'])
        msgs = msg_schema.dump(fetched)
        return response_with(resp.SUCCESS_200, value={'messages': msgs})
    elif (second is not None):
        fetched = Messages.query.filter_by(room_name=second.room_name).all()
        msg_schema = MessageSchema(many=True, only=['message', 'sender_id', 'receiver_id'])
        msgs = msg_schema.dump(fetched)
        return response_with(resp.SUCCESS_200, value={'messages': msgs})
    else:
        return response_with(resp.BAD_REQUEST_400)

@message_routes.route('/send/message/to/chat/room/<room_name>', methods = ['post'])
def send_message(room_name, sender_id, receiver_id, message):
    data = {}
    data['room_name'] = room_name
    data['sender_id'] = sender_id
    data['receiver_id'] = receiver_id
    data['message'] = message
    msg_schema = MessageSchema()
    msg = msg_schema.load(data)
    result = msg_schema.dump(msg.create())
    return response_with(resp.SUCCESS_200, value={'message' : result})   

@message_routes.route('/<int:message_id>', methods = ['get'])
def get_message_detail(message_id):
    fetched = Messages.query.get_or_404(message_id)
    msg_schema = MessageSchema()
    msg = msg_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={'message': msg})

@message_routes.route('/send/request/message/<int:user_id>', methods=['post'])
def send_request_message(user_id):
    data = request.get_json()
    data['message'] = 'Friend Request Sent Wait for Response'
    data['sender_id']=user_id
    msg_schema = MessageSchema()
    msg = msg_schema.load(data)
    result = msg_schema.dump(msg.create())
    return response_with(resp.SUCCESS_200, value={'message': result})
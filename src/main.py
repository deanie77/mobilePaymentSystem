import os, sys, logging, random, string
from flask import Flask, jsonify
from flask.helpers import send_from_directory
from flask_jwt_extended import JWTManager
from sqlalchemy.sql.elements import or_, and_
from api.config.config import *
from api.models.friendships import Friendships
from api.models.messages import Messages
from api.utils.database import db
from api.utils.responses import response_with
from api.routes.friendships import friendship_routes, update_friendship_status
from api.routes.wallets import confirm_receipt, pay_money, wallet_routes
from api.routes.cards import card_routes
from api.routes.messages import create_chat_room, message_routes, send_message
from api.routes.transactions import create_transaction, transaction_routes
from api.routes.banks import bank_routes
from api.routes.board_of_directors import bOd_routes
from api.routes.bank_cards import bank_card_routes
from api.routes.users import user_routes
from api.utils.email import mail
import api.utils.responses as resp
from flask_socketio import SocketIO, join_room

app = Flask(__name__)

if os.environ.get('WORK_ENV') == 'PROD':
    app_config = ProductionConfig
elif os.environ.get('WORK_ENV') == 'TEST':
    app_config = TestingConfig
else:
    app_config = DevelopmentConfig

@app.route('/avatar/<filename>')
def  uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

app.config.from_object(app_config)
app.config.from_pyfile('api\config\config.py')

app.register_blueprint(user_routes, url_prefix='/api/users')
app.register_blueprint(wallet_routes, url_prefix='/api/wallets')
app.register_blueprint(friendship_routes, url_prefix='/api/friendships')
app.register_blueprint(card_routes, url_prefix='/api/cards')
app.register_blueprint(bank_routes, url_prefix='/api/banks')
app.register_blueprint(bank_card_routes, url_prefix='/api/bank_cards')
app.register_blueprint(bOd_routes, url_prefix='/api/directors')
app.register_blueprint(message_routes, url_prefix='/api/messages')
app.register_blueprint(transaction_routes, url_prefix='/api/transactions')

socketio = SocketIO(app, cors_allowed_origins='*')

@socketio.on('send_request')
def handle_send_request_event(data):
    app.logger.info('{} has sent message to user {}'.format(data['user_one'],
                                                            data['user_two']))

    if (Messages.find_by_user_one(data['user_one'], data['user_two']) is not None
        or Messages.find_by_user_two(data['user_one'], data['user_two']) is not None):
       return response_with(resp.BAD_REQUEST_400)
    else:
        room_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for value in range(7))  
        create_chat_room(data['user_one'], data['user_two'], room_name=room_name)  
        join_room(room_name)
        socketio.emit('receive_request', data, room=room_name)

@socketio.on('accept_request')
def handle_accept_friend_request(data):
    app.logger.info('{} accepted {}\'s friend request'.format(data['user_id'],
                                                                data['other_id']))
    update_friendship_status(data['user_id'], data['other_id'])
    first = Messages.find_by_user_one(data['user_id'], data['other_id'])
    second = Messages.find_by_user_two(data['user_id'], data['other_id'])
    if (first is not None):
        room_name = first.room_name
        message = 'Friend Request Accepted'
        send_message(room_name, data['user_id'], data['other_id'], message)
        join_room(room_name)
        socketio.emit('message', message, room=room_name)
    elif (second is not None):
        room_name = second.room_name
        message = 'Friend Request Accepted'
        send_message(room_name, data['user_id'], data['other_id'], message)
        join_room(room_name)
        socketio.emit('message', message, room=room_name)

@socketio.on('send_message')
def handle_send_message_event(data):
    first = Messages.find_by_user_one(data['user_id'], data['other_id'])
    second = Messages.find_by_user_two(data['user_id'], data['other_id'])
    friend_one = Friendships.find_if_request_exists(data['user_id'], data['other_id'])
    friend_two = Friendships.find_if_request_exists_reverse(data['user_id'], data['other_id'])
    if (friend_one is not None ):
        if(friend_one.status == 1):
            if (first is not None):
                room_name = first.room_name
                send_message(room_name, data['user_id'], data['other_id'], data['message'])
                socketio.emit('send_message', data['message'], room=room_name)
            elif (second is not None):
                room_name = second.room_name
                send_message(room_name, data['user_id'], data['other_id'], data['message'])
                socketio.emit('send_message', data['message'], room=room_name)
        else:
            return response_with(resp.BAD_REQUEST_400, value={'message': 'you are not yet friends'})
    if (friend_two is not None ):
        if(friend_two.status == 1):
            if (first is not None):
                room_name = first.room_name
                send_message(room_name, data['user_id'], data['other_id'], data['message'])
                socketio.emit('send_message', data['message'], room=room_name)
            elif (second is not None):
                room_name = second.room_name
                send_message(room_name, data['user_id'], data['other_id'], data['message'])
                socketio.emit('send_message', data['message'], room=room_name)
        else:
            return response_with(resp.BAD_REQUEST_400, value={'message': 'you are not yet friends'})
    else:
        return response_with(resp.BAD_REQUEST_400)

@socketio.on('send_money')
def handle_send_money_event(data):
    first = Messages.find_by_user_one(data['user_id'], data['other_id'])
    second = Messages.find_by_user_two(data['user_id'], data['other_id'])
    friend_one = Friendships.find_if_request_exists(data['user_id'], data['other_id'])
    friend_two = Friendships.find_if_request_exists_reverse(data['user_id'], data['other_id'])
    if (friend_one is not None ):
        if(friend_one.status == 1):
            if (first is not None):
                room_name = first.room_name
                pay_money(data['other_id'], data['user_id'], data['amount'], data['password'])
                confirm_receipt(data['other_id'], data['amount'])
                message = 'Sent ${}'.format(data['amount'])
                transaction_type = 'money transfer'
                status = 'successful'
                create_transaction(data['user_id'], data['other_id'], data['amount'], transaction_type, status)
                send_message(room_name, data['user_id'], data['other_id'], message)
                socketio.emit('send_message', message, room=room_name)
            elif (second is not None):
                room_name = first.room_name
                pay_money(data['other_id'], data['user_id'], data['amount'])
                confirm_receipt(data['other_id'], data['amount'])
                message = 'Sent ${}'.format(data['amount'])
                transaction_type = 'money transfer'
                status = 'successful'
                create_transaction(data['user_id'], data['other_id'], data['amount'], transaction_type, status)
                send_message(room_name, data['user_id'], data['other_id'], message)
                socketio.emit('send_message', message, room=room_name)
        else:
            return response_with(resp.BAD_REQUEST_400, value={'message': 'you are not yet friends'})
    if (friend_two is not None ):
        if(friend_two.status == 1):
            if (first is not None):
                room_name = first.room_name
                pay_money(data['other_id'], data['user_id'], data['amount'], data['password'])
                confirm_receipt(data['other_id'], data['amount'])
                message = 'Sent ${}'.format(data['amount'])
                transaction_type = 'money transfer'
                status = 'successful'
                create_transaction(data['user_id'], data['other_id'], data['amount'], transaction_type, status)
                send_message(room_name, data['user_id'], data['other_id'], message)
                socketio.emit('send_message', message, room=room_name)
            elif (second is not None):
                room_name = first.room_name
                pay_money(data['other_id'], data['user_id'], data['amount'])
                confirm_receipt(data['other_id'], data['amount'])
                message = 'Sent ${}'.format(data['amount'])
                transaction_type = 'money transfer'
                status = 'successful'
                create_transaction(data['user_id'], data['other_id'], data['amount'], transaction_type, status)
                send_message(room_name, data['user_id'], data['other_id'], message)
                socketio.emit('send_message', message, room=room_name)
        else:
            return response_with(resp.BAD_REQUEST_400, value={'message': 'you are not yet friends'})
    else:
        transaction_type = 'money transfer'
        status = 'failed'
        create_transaction(data['user_id'], data['other_id'], data['amount'], transaction_type, status)

@app.after_request
def add_header(response):
    return response

@app.errorhandler(400)
def bad_request(e):
    logging.error(e)
    return response_with(resp.BAD_REQUEST_400) 

@app.errorhandler(500)
def server_error(e):
    logging.error(e)
    return response_with(resp.SERVER_ERROR_500)

@app.errorhandler(404)
def not_found(e):
    logging.error(e)
    return response_with(resp. SERVER_ERROR_404)

jwt = JWTManager(app)
mail.init_app(app)

db.init_app(app)
with app.app_context():
    db.create_all()

logging.basicConfig(stream=sys.stdout, format='%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s|%(message)s', level=logging.DEBUG)
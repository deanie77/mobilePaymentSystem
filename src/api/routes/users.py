import os, json
from flask.globals import session
from flask_jwt_extended.view_decorators import jwt_required
from sqlalchemy.orm.query import Query
from api.models.wallets import Wallet
from flask import Blueprint, request, current_app, Response, redirect, url_for,render_template_string
from werkzeug.utils import html, redirect, secure_filename
from api.utils.responses import SERVER_ERROR_404, response_with
from api.utils import responses as resp
from api.models.users import User, UserSchema
from api.utils.database import db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required
from api.utils.token import generate_verification_token, confirm_verification_token
from api.utils.email import send_email

user_routes = Blueprint('user_routes', __name__)

def jsonResponseFactory(data):
    '''Return a callable in top of Response'''
    def callable(response=None, *args, **kwargs):
        '''Return a response with JSON data from factory context'''
        return Response(json.dumps(data), *args, **kwargs)
    return callable

@user_routes.route('/', methods = ['post'])
def create_user():
    try:
        data = request.get_json()
        if(User.find_by_email(data['email']) is not None or
        User.find_by_username(data['username']) is not None):
            return response_with(resp.INVALID_INPUT_422)
        data['password'] = User.generate_hash(data['password'])
        user_schema = UserSchema()
        user = user_schema.load(data)
        token = generate_verification_token(data['email'])
        verification_email = url_for('user_routes.verify_email', token=token, _external=True)
        html = render_template_string('<p>Welcome! Thanks for signing up. Please follow this link to activate your account:</p> <p><a href="{{ verification_email }}">{{ verification_email }}</a></p> <br> <p>Thanks!</p>',
        verification_email=verification_email)
        subject = 'please verify your email'
        send_email(user.email, subject, html)
        result = user_schema.dump(user.create())
        return response_with(resp.SUCCESS_200, value={'user_id': user.id})
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)

@user_routes.route('/confirm/<token>', methods = ['get'])
def verify_email(token):
    try:
        email = confirm_verification_token(token)
    except:
        return response_with(resp.SERVER_ERROR_401)
    
    user = User.query.filter_by(email=email).first_or_404()
    if user.isVerified:
        return response_with(resp.INVALID_INPUT_422)
    else:
        user.isVerified = True
        db.session.add(user)
        db.session.commit()
        return response_with(resp.SUCCESS_200, value={'message': 'email verified, you can proceed to login now.'})
        
@user_routes.route('/login', methods = ['post'])
def authenricate_user():
    try:
        data = request.get_json()
        current_user = User.find_by_email(data['email'])
        if not current_user:
            return response_with(resp.SERVER_ERROR_404)
        if current_user and not current_user.isVerified:
            return response_with(resp.BAD_REQUEST_400)
        if User.verify_hash(data['password'], current_user.password):
            user_id = current_user.id
            access_token = create_access_token(identity = current_user.email)
            refresh_token = create_refresh_token(current_user.email)
            return response_with(resp.SUCCESS_201, value = {'message': 'Logged in as {}'. format(current_user.username), 'access_token': access_token, 'refresh_token': refresh_token, 'user_id': user_id})
        else:
            return response_with(resp.UNAUTHORIZED_401)
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)


@user_routes.route('/all/users', methods = ['get'])
def get_user_list():
    fetched = User.query.all()
    user_schema = UserSchema(many=True, only=['first_name', 'last_name', 'id'])
    users = user_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={'users': users})

@user_routes.route('/retrieve/user/<int:user_id>', methods = ['get'])
def get_user_detail(user_id):
    fetched = User.query.get_or_404(user_id)
    user_schema = UserSchema(only=['first_name', 'last_name', 'username'])
    user = user_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={'user': user})

@user_routes.route('/renew/<int:user_id>', methods = ['put'])
def update_user_detail(user_id):
    data = request.get_json()
    get_user = User.query.get_or_404(user_id)
    if data.get('username'):
        get_user.username = data['username']
    if data.get('phonenumber'):
        get_user.phonenumber = data['phonenumber']
    db.session.add(get_user)
    db.session.commit()
    user_schema = UserSchema()
    user = user_schema.dump(get_user)
    return response_with(resp.SUCCESS_200, value={'user': user})

@user_routes.route('/change/<int:user_id>', methods = ['patch'])
def modify_user_detail(user_id):
    data = request.get_json()
    get_user = User.query.get(user_id)
    if data.get('phonenumber'):
        get_user.phonenumber = data['phonenumber']
    if data.get('username'):
        get_user.username = data['username']
    db.session.add(get_user)
    db.session.commit()
    user_schema = UserSchema()
    user = user_schema.dump(get_user)
    return response_with(resp.SUCCESS_200, value={'user': user})

@user_routes.route('delete/user/<int:user_id>', methods = ['delete'])
def delete_user(user_id):
    get_user = User.query.get_or_404(user_id)
    db.session.delete(get_user)
    db.session.commit()
    return response_with(resp.SUCCESS_204)

@user_routes.route('/register/wallet/<int:user_id>', methods=['get'])
def register_wallet(user_id):
    try:
        get_user = User.query.get_or_404(user_id)
        if get_user:
            return redirect(url_for('wallet_routes.create_wallet', user_id=user_id))
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400)
        
@user_routes.route('/user/wallet/<int:user_id>', methods=['get'])
@jwt_required
def get_user_wallet(user_id):
    return redirect(url_for('wallet_routes.get_wallet_detail', user_id=user_id))

@user_routes.route('/user/wallet/topup/<int:user_id>', methods=['post'])
@jwt_required
def user_topup_wallet(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    if user.verify_hash(data['password'], user.password):
        return redirect(url_for('wallet_routes.topup_wallet', card_number=data['card_number'], amount=data['amount']))

@user_routes.route('/user/wallet/withdraw/<int:user_id>', methods=['post'])
@jwt_required
def withdraw_from_wallet(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    if User.verify_hash(data['password'], user.password):
        print(data)
        return redirect(url_for('wallet_routes.withdraw_wallet', amount=data['amount'], card_number=data['card_number']))

@user_routes.route('/find/user/<username>', methods = ['get'])
@jwt_required
def get_searched_user(username):
    fetched = User.query.filter_by(username=username).all()
    user_schema = UserSchema(many=True, only=['username', 'email', 'id'])
    users = user_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={'users': users})

@user_routes.route('requester/<int:user_id>', methods = ['get'])
@jwt_required
def find_friend_requester(user_id):
    fetched = User.query.get_or_404(user_id)
    user_schema = UserSchema(only=['username', 'email', 'id'])
    user = user_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={'user': user})

@user_routes.route('chat/list/user/info/<int:user_id>', methods = ['get'])
@jwt_required
def get_users_on_list_info(user_id):
    fetched = User.query.get_or_404(user_id)
    user_schema = UserSchema(only=['username', 'avatar', 'email', 'id'])
    user = user_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={'user': user})

@user_routes.route('myprofile/<int:user_id>', methods = ['get'])
@jwt_required
def get_profile_details(user_id):
    fetched = User.query.get_or_404(user_id)
    user_schema = UserSchema(only=['first_name', 'last_name', 'username', 'email'])
    user = user_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={'user': user})

@user_routes.route('/logout', methods=['get'])
def logout():
    session.clear()
    return response_with(resp.SUCCESS_200)
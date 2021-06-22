from flask import Blueprint, json, request
from flask.helpers import url_for
from flask_jwt_extended import jwt_required
from werkzeug.utils import redirect
from api.models.users import User
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.wallets import Wallet, WalletSchema
from api.utils.database import db

wallet_routes = Blueprint('wallet_routes', __name__)

@wallet_routes.route('/<int:user_id>', methods=['get'])
def create_wallet(user_id):
    try:
        json_data = {
            'balance': 0,
            'user_id': 0
        }
        string_data = json.dumps(json_data)
        data = json.loads(string_data)
        data['balance'] = 0.00
        data['user_id'] = user_id
        wallet_schema = WalletSchema()
        wallet = wallet_schema.load(data)
        result = wallet_schema.dump(wallet.create())
        return response_with(resp.SUCCESS_201, value={'wallet': result}) 
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)

@wallet_routes.route('/', methods = ['get'])
def get_wallet_list():
    fetched = Wallet.query.all()
    wallet_schema = WalletSchema(many=True, only=['balance', 'id', 'user_id'])
    wallets = wallet_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={'wallets': wallets})

@wallet_routes.route('/get/wallet/<int:user_id>', methods = ['get'])
def get_wallet_detail(user_id):
    fetched = Wallet.query.filter_by(user_id=user_id).first()
    wallet_schema = WalletSchema()
    wallet = wallet_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={'wallet': wallet})

@wallet_routes.route('/balance/<int:wallet_id>', methods=['get'])
def check_balance(wallet_id):
    fetch = Wallet.query.get_or_404(wallet_id)
    balance = fetch.balance
    return response_with(resp.SUCCESS_200, value={'wallet balance': balance})

@wallet_routes.route('/topup/<card_number>/<float:amount>', methods=['get'])
def topup_wallet(card_number, amount):
    return redirect(url_for('card_routes.withdraw_money', amount=amount, card_number=card_number))

@wallet_routes.route('/confirm_topup/<float:amount>/<int:wallet_id>', methods=['get'])
def confirm_topup(amount, wallet_id):
    get_wallet = Wallet.query.get(wallet_id)
    get_wallet.balance += amount
    db.session.add(get_wallet)
    db.session.commit()
    wallet = WalletSchema()
    result = wallet.dump(get_wallet)
    return response_with(resp.SUCCESS_200, value={'added': result})

@wallet_routes.route('/withdraw/<float:amount>/<card_number>', methods=['get'])
def withdraw_wallet(amount, card_number):
    return redirect(url_for('card_routes.money_to_bank', card_number=card_number, amount=amount))

@wallet_routes.route('/confirm_withdrawal/<int:wallet_id>/<float:amount>', methods=['get']) 
def confirm_withdrawal(wallet_id, amount):
    wallet = Wallet.query.get_or_404(wallet_id)
    wallet.balance -= amount
    db.session.add(wallet)
    db.session.commit()
    return response_with(resp.SUCCESS_200, value={'new wallet balance': wallet.balance})

@wallet_routes.route('/receive_money/<int:user_id>/<int:sender_id>', methods=['get'])
def receive_money(user_id, sender_id):
    data = request.get_json()
    return redirect(url_for('wallet_routes.pay_money', user_id=user_id, sender_id=sender_id, amount=data['amount']))

@wallet_routes.route('/pay_money/<int:user_id>/<int:sender_id>/<float:amount>', methods=['get'])
def pay_money(user_id, sender_id, amount, password):
    sender_wallet = Wallet.query.filter_by(user_id=sender_id).first()
    sender = User.query.get_or_404(sender_id)
    if User.verify_hash(password, sender.password):
        if sender_wallet.balance >= amount:
            sender_wallet.balance -= amount
            db.session.add(sender_wallet)
            db.session.commit()
            return response_with(resp.SUCCESS_200)
        else:
            return response_with(resp.BAD_REQUEST_400, value={'message': 'insufficient funds'})
    else:
        response_with(resp.BAD_REQUEST_400, value={'message': 'wrong password'})

@wallet_routes.route('/confirm_receipt/<int:user_id>', methods=['get'])
def confirm_receipt(user_id, amount):
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    wallet.balance += amount
    db.session.add(wallet)
    db.session.commit()
    return response_with(resp.SUCCESS_200, value={'new wallet balance': wallet.balance})

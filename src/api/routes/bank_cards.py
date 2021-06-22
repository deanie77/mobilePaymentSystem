from flask import Blueprint, json, request, current_app, url_for
from flask_jwt_extended import jwt_required
from werkzeug.utils import redirect, secure_filename
from api.models.banks import Banks
from api.utils import token
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.bank_cards import BankCards, BankCardsSchema
from api.utils.database import db

bank_card_routes = Blueprint('bank_card_routes', __name__)

@bank_card_routes.route('/', methods=['post'])
def upload_bank_cards():
    data = request.get_json()
    if (Banks.query.filter_by(bank_name=data['bank_name']).first() is not None):
        bankcard_schema = BankCardsSchema()
        bank_card = bankcard_schema.load(data)
        result = bankcard_schema.dumps(bank_card.create())
        return response_with(resp.SUCCESS_200, value={'bank_card': result})
    else:
        return response_with(resp.BAD_REQUEST_400, value={'message': 'bank does not exist'})

@bank_card_routes.route('/<string:bank_card_number>/<int:card_id>', methods = ['get'])
def get_user_detail(bank_card_number, card_id):
    fetched = BankCards.query.filter_by(card_number=bank_card_number).first()
    fetched.card_status = 'connected'
    db.session.add(fetched)
    db.session.commit()
    return redirect(url_for('card_routes.finish_confirmation', card_id=card_id, cardnumber=bank_card_number))

@bank_card_routes.route('/withraw/<string:bank_id>/<float:amount>/<int:wallet_id>', methods=['get'])
def withdraw_bank(bank_id, amount, wallet_id):
    fetched = BankCards.query.filter_by(card_number=bank_id).first()
    if fetched.card_status == 'connected':
        if fetched.account_balance >= amount:
            fetched.account_balance = fetched.account_balance - amount
            db.session.add(fetched)
            db.session.commit()
            return redirect(url_for('wallet_routes.confirm_topup', amount=amount,wallet_id=wallet_id))
        else:
            return response_with(resp.BAD_REQUEST_400, value={'message': 'insufficient credit'})
    else:
        return response_with(resp.INVALID_INPUT_422)

@bank_card_routes.route('/back_to_bank/<bank_id>/<float:amount>/<int:wallet_id>', methods=['get'])
def send_to_bank(bank_id, amount, wallet_id):
    fetched = BankCards.query.filter_by(card_number=bank_id).first()
    if fetched.card_status == 'connected':
        fetched.account_balance += amount
        db.session.add(fetched)
        db.session.commit()
        return redirect(url_for('wallet_routes.confirm_withdrawal', wallet_id=wallet_id, amount=amount))
    else:
        return response_with(resp.INVALID_INPUT_422)
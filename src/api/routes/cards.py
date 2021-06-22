from flask import Blueprint, json, request, current_app, url_for
from flask_jwt_extended import jwt_required
from sqlalchemy.sql.expression import null
from werkzeug.utils import redirect
from api.models.wallets import Wallet
from api.utils import token
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.card_token import CardToken, CardTokenSchema
from api.models.bank_cards import BankCards
from flask_jwt_extended import create_access_token, create_refresh_token
from api.utils.token import generate_verification_token, confirm_verification_token
from api.utils.database import db
from sqlalchemy import text

card_routes = Blueprint('card_routes', __name__)

@card_routes.route('add/card/<int:user_id>', methods=['post'])
@jwt_required
def add_card(user_id):
    data = request.get_json()
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    token= CardToken.encode_auth_token(data['card_number'], data['card_type'], data['card_provider'], data['bank_name'], 
    data['expiry_date'], data['cvv_code'], data['card_holder_name'], data['user_id_type'], data['user_id'], 
    data['phonenumber'], data['user_agreement'], data['address_1'], data['address_2'], data['zip_code'], data['city'], data['country'])
    data['status'] = 'waiting'
    data['token'] = token
    data['wallet_id'] = wallet.id
    card_token_schema = CardTokenSchema()
    card = card_token_schema.load(data)
    result = card_token_schema.dump(card.create())
    return redirect(url_for('card_routes.confirm_card', card_id=card.id))

@card_routes.route('/verify_card/<int:card_id>', methods=['get'])
def confirm_card(card_id):
    try:
        card = CardToken.query.get(card_id)
        payload = CardToken.verify_card(card.token)
        return redirect(url_for('bank_card_routes.get_user_detail', bank_card_number=payload['card_number'], card_id=card_id))
    except:
        return response_with(resp.SERVER_ERROR_404)

@card_routes.route('/finish_card_confirmation/<int:card_id>/<string:cardnumber>', methods=['get'])
def finish_confirmation(card_id, cardnumber):
    try:
        card = CardToken.query.get(card_id)
        card.cardnumber = cardnumber
        card.status = 'connected'
        db.session.add(card)
        db.session.commit()
        return response_with(resp.SUCCESS_200, value={'message': 'card connected'})
    except:
        return response_with(resp.INVALID_INPUT_422)

@card_routes.route('/withdraw/<float:amount>/<card_number>', methods=['get'])
def withdraw_money(amount, card_number):
    try:
        card = CardToken.query.filter_by(cardnumber=card_number).first()
        if card.status == 'connected' and card.cardnumber is not null:
            payload = CardToken.verify_card(card.token)
            return redirect(url_for('bank_card_routes.withdraw_bank', bank_id=payload['card_number'], amount=amount, wallet_id=card.wallet_id))
    except:
        return response_with(resp.SERVER_ERROR_404)

@card_routes.route('/to_bank/<card_number>/<float:amount>', methods=['get'])
def money_to_bank(card_number, amount):
    try:
        card = CardToken.query.filter_by(cardnumber=card_number).first()
        if card.status == 'connected' and card.cardnumber is not null:
            payload = CardToken.verify_card(card.token)
            return redirect(url_for('bank_card_routes.send_to_bank', bank_id=card.cardnumber, amount=amount, wallet_id=card.wallet_id))
    except:
        return response_with(resp.INVALID_INPUT_422)
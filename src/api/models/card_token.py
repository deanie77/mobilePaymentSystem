from functools import wraps
from api.utils.database import db
from passlib.hash import pbkdf2_sha256 as sha256
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from flask import current_app
import jwt

class CardToken(db.Model):
    __tablename__ = 'card_token'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Text, nullable=False)
    made = db.Column(db.DateTime, server_default=db.func.now())
    status = db.Column(db.String(20), default='waiting')
    cardnumber = db.Column(db.String(100), nullable=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'))

    def __init__(self, token, wallet_id, status):
        self.token = token
        self.wallet_id = wallet_id
        self.status = status

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @staticmethod
    def encode_auth_token(card_number, card_type, card_provider, bank_name,expiry_date, cvv_code,
     card_holder_name, user_id_type, user_id, phonenumber, user_agreement, address_1, 
    address_2, zip_code, city, country ):
        try:
            payload = {
                'card_number': card_number,
                'card_type': card_type,
                'card_provider':card_provider,
                'bank_name': bank_name,
                'expiry_date': expiry_date,
                'cvv_code': cvv_code,
                'card_holder_name': card_holder_name,
                'user_id_type': user_id_type,
                'user_id': user_id,
                'phonenumber': phonenumber,
                'user_agreement': user_agreement,
                'address_1': address_1,
                'address_2':address_2,
                'zip_code': zip_code, 
                'city': city,
                'country': country
            }
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return token
        except Exception as e:
            return e

    @staticmethod
    def verify_card(token):
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'])
            return payload
        except jwt.InvalidTokenError:
            return 'invalid token. please enter password again'

class CardTokenSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = CardToken
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    made = fields.DateTime(dump_only=True)
    token = fields.String()
    cvv_code = fields.String(required=True)
    card_type = fields.String(required=True)
    card_number = fields.String(required=True)
    card_provider = fields.String(required=True)
    expiry_date = fields.Date(required=True)
    bank_name = fields.String(required = True)
    card_holder_name = fields.String(required = True)
    user_id_type = fields.String(required=True)
    user_id = fields.String(required = True)
    phonenumber = fields.String(required = True, unique = True, nullable = False)
    wallet_id = fields.Integer()
    address_1 = fields.String(required=True)
    address_2 = fields.String(required=True)
    city = fields.String(required=True)
    country = fields.String(required=True)
    zip_code = fields.String(required=True)
    user_agreement = fields.Boolean(required=True)
    status = fields.String()
    cardnumber = fields.String()
from flask_sqlalchemy import model
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from passlib.hash import pbkdf2_sha256 as sha256

class BankCards(db.Model):
    __tablename__ = 'bank_cards'

    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(150), nullable=False)
    card_type = db.Column(db.String(20), nullable=False)
    card_provider = db.Column(db.String(50), nullable=False)
    bank_name = db.Column(db.String(50), db.ForeignKey('banks.bank_name'), nullable=False)
    cvv_code = db.Column(db.String(150), nullable=False)
    expiry_date = db.Column(db.Date, nullable=True)
    account_balance = db.Column(db.Float, nullable=False)
    card_status = db.Column(db.String(50), nullable=False, default='pending')
    card_holder_name = db.Column(db.String(120), nullable=False)
    user_id_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(120), nullable=False)
    phonenumber = db.Column(db.String(20), nullable=False)
    address_1 = db.Column(db.String(150), nullable=False)
    address_2 = db.Column(db.String(150), nullable=False)
    zip_code = db.Column(db.String(15), nullable=False)
    city = db.Column(db.String(150), nullable=False)
    country = db.Column(db.String(120), nullable=False)

    def __init__(self, card_number, card_provider, card_type, bank_name,expiry_date, cvv_code, account_balance, card_holder_name, user_id_type, user_id, phonenumber, address_1, address_2, zip_code, city, country):
        self.card_number = card_number
        self.card_type = card_type
        self.card_provider = card_provider
        self.bank_name = bank_name
        self.expiry_date = expiry_date
        self.cvv_code = cvv_code
        self.account_balance = account_balance
        self.card_holder_name = card_holder_name
        self.user_id_type = user_id_type
        self.user_id = user_id
        self.phonenumber = phonenumber
        self.address_1 = address_1
        self.address_2 = address_2
        self.city = city
        self.country = country
        self.zip_code = zip_code

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_card_number(cls, card_number):
        return cls.query.filter_by(card_number = card_number).first()

class BankCardsSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = BankCards
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    card_number = fields.String(required=True)
    card_type = fields.String(required=True)
    card_provider = fields.String(required=True)
    cvv_code = fields.String(required=True)
    expiry_date = fields.Date(required=True)
    account_balance = fields.Float(required=True)
    bank_name = fields.String(required = True)
    card_holder_name = fields.String(required = True)
    user_id_type = fields.String(required=True)
    user_id = fields.String(required = True)
    phonenumber = fields.String(required = True, unique = True, nullable = False)
    address_1 = fields.String(required=True)
    address_2 = fields.String(required=True)
    city = fields.String(required=True)
    country = fields.String(required=True)
    zip_code = fields.String(required=True)
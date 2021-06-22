from flask_sqlalchemy import model
from sqlalchemy.orm import backref
from api.models.bank_cards import BankCardsSchema
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from api.models.board_of_directors import BODSchema
from passlib.hash import pbkdf2_sha256 as sha256

class Banks(db.Model):
    __tablename__ = 'banks'

    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(150), nullable=False, unique=True)
    bank_email = db.Column(db.String(150), nullable=False, unique=True)
    contact_number = db.Column(db.String(20), nullable=False)
    bank_type = db.Column(db.String(150), nullable=False)
    address_1 = db.Column(db.String(150), nullable=False)
    address_2 = db.Column(db.String(150), nullable=False)
    zip_code = db.Column(db.String(15), nullable=False)
    city = db.Column(db.String(150), nullable=False)
    country = db.Column(db.String(150), nullable=False)
    utility_bills = db.Column(db.String(150), nullable=True)
    certificate_of_incorporation = db.Column(db.String(150), nullable=True)
    bank_statement = db.Column(db.String(150), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, server_default=db.func.now())
    password = db.Column(db.String(120), nullable=False)
    directors = db.relationship('BoardOfDirectors', backref='Banks', cascade='all, delete-orphan')
    cards = db.relationship('BankCards', backref='Banks', cascade='all, delete-orphan')

    def __init__(self, bank_name, bank_email, contact_number, bank_type, address_1, address_2, zip_code, city, country, password):
        self.bank_name = bank_name
        self.bank_email = bank_email
        self.contact_number = contact_number
        self.password = password
        self.bank_type = bank_type
        self.address_1 = address_1
        self.address_2 = address_2
        self.zip_code = zip_code
        self.city = city
        self.country = country

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_bank(cls, bank_name):
        return cls.query.filter_by(bank_name = bank_name).first()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

class BankSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Banks
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    bank_name = fields.String(required=True)
    bank_email = fields.String(required=True)
    contact_number = fields.String(required=True)
    password = fields.String(required=True)
    bank_type = fields.String(required=True)
    address_1 = fields.String(required=True)
    address_2 = fields.String(required=True)
    zip_code = fields.String(required=True)
    city = fields.String(required=True)
    country = fields.String(required=True)
    utility_bills = fields.String(dump_only=True)
    certificate_of_incorporation = fields.String(dump_only=True)
    bank_statement = fields.String(dump_only=True)
    created = fields.DateTime(dump_only=True)
    directors = fields.Nested(BODSchema, many=True, only=['first_name', 'last_name', 'email', 'phonenumber'])
    cards = fields.Nested(BankCardsSchema, many=True, only=['card_type', 'card_status', 'card_holder_name', 'card_provider'])
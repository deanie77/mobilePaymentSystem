from enum import unique
from flask_sqlalchemy import model
from sqlalchemy.orm import backref
from api.utils.database import db
from passlib.hash import pbkdf2_sha256 as sha256
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from api.models.wallets import WalletSchema
from api.models.messages import MessageSchema

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    username = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(120), nullable = False)
    isVerified = db.Column(db.Boolean, nullable = False, default = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    phonenumber = db.Column(db.String(30), unique=True, nullable=False)
    avatar = db.Column( db.String(200), nullable=True)
    joined = db.Column(db.DateTime, server_default=db.func.now())
    wallet = db.relationship('Wallet', uselist=False, backref='User', cascade='all, delete-orphan')
    followed = db.relationship('User', secondary='friendships', primaryjoin='User.id==friendships.c.user_one', secondaryjoin='User.id==friendships.c.user_two', backref='followers')

    def __init__(self, first_name, last_name, date_of_birth, username, email, phonenumber, password):
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.username = username
        self.password = password
        self.email = email
        self.phonenumber = phonenumber

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email = email).first()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username = username).first()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

class UserSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = User
        sqla_session = db.session

    id = fields.Number(dump_only = True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    username = fields.String(required = True)
    email = fields.String(required=True, nullable = False)
    phonenumber = fields.String(required = True, unique = True, nullable = False)
    joined = fields.DateTime(dump_only=True)
    avatar = fields.String(dump_only=True)
    wallet = fields.Nested(WalletSchema, only=['id', 'balance'])
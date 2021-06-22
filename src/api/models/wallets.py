from sqlalchemy.orm import backref
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from api.models.card_token import CardTokenSchema

class Wallet(db.Model):
    __tablename__ = 'wallets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    balance = db.Column(db.Float, default=0.00)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cards = db.relationship('CardToken', backref='Wallet', cascade='all, delete-orphan')

    def __init__(self, balance, user_id=None):
        self.balance = balance
        self.user_id = user_id

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class WalletSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Wallet
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    balance = fields.Float()
    user_id = fields.Integer()
    cards = fields.Nested(CardTokenSchema, many=True, only=['made', 'status', 'cardnumber', 'id'])
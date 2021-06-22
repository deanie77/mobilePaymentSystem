from flask_sqlalchemy import model
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

class UserBanking(db.Model):
    __tablename__ = 'user_banking'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    card_number = db.Column(db.String(150), db.ForeignKey('bank_cards.card_number'))
    balance_before = db.Column(db.Float, db.ForeignKey('bank_cards.account_balance'))
    amount = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, db.ForeignKey('bank_cards.account_balance'))
    participant_id = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), default='pending')

    def __init__(self, user_id, card_number, balance_before, amount, balance_after, participant_id, status):
        self.user_id = user_id
        self.card_number = card_number
        self.balance_after = balance_after
        self.balance_before = balance_before
        self.amount = amount
        self.participant_id = participant_id
        self.status = status

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class UserBankingSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = UserBanking
        sqla_session = db.session

    user_id = fields.Integer(required=True)
    card_number = fields.String(required=True)
    balance_before = fields.Float(required=True)
    amount = fields.Float(required=True)
    balance_after = fields.Float(required=True)
    participant_id = fields.String(required=True)
    status = fields.String(required=True)
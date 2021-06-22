from flask_sqlalchemy import model
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

class Transactions(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    payee = db.Column(db.String(120), db.ForeignKey('users.username'),nullable=False)
    payer = db.Column(db.String(120), db.ForeignKey('users.username'),nullable=False)
    created = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, transaction_type, amount, status, payee, payer):
        self.transaction_type = transaction_type
        self.amount = amount
        self.status = status
        self.payee = payee
        self.payer = payer

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class TransactionSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Transactions
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    transaction_type = fields.String(required=True)
    amount = fields.Float(required=True)
    status = fields.String(required=True)
    payee = fields.String(required=True)
    payer = fields.String(required=True)
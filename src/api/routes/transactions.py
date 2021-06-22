from flask import Blueprint, json, request
from flask_jwt_extended import jwt_required
from sqlalchemy.sql.expression import or_
from api.models.users import User
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.transactions import Transactions, TransactionSchema

transaction_routes = Blueprint('transaction_routes', __name__)

@transaction_routes.route('/create/money/transaction/<int:user_id>/<int:other_id>/<float:amount>', methods=['post'])
def create_transaction(user_id, other_id, amount, transaction_type, status):
    data = {}
    payer = User.query.get_or_404(user_id)
    payee = User.query.get_or_404(other_id)
    data['payer'] = payer.username
    data['payee'] = payee.username
    data['amount'] = amount
    data['transaction_type'] = transaction_type
    data['status'] = status
    trans_schema = TransactionSchema()
    trans = trans_schema.load(data)
    result = trans_schema.dump(trans.create())
    return response_with(resp.SUCCESS_200, value={'Transaction' : result})

@transaction_routes.route('/get/transaction/history/<int:user_id>', methods=['get'])
@jwt_required
def get_transactions(user_id):
    user = User.query.get_or_404(user_id)
    transactions = Transactions.query.filter(or_(Transactions.payer.like(user.username), Transactions.payee.like(user.username)))
    trans_schema = TransactionSchema(many=True)
    result = trans_schema.dump(transactions)
    return response_with(resp.SUCCESS_200, value={'transaction': result})

@transaction_routes.route('/income/expense/<int:user_id>', methods=['get'])
@jwt_required
def income_expenses(user_id):
    data = {}
    expenses = 0
    income = 0
    user = User.query.get_or_404(user_id)
    transactions = Transactions.query.filter(or_(Transactions.payer.like(user.username), Transactions.payee.like(user.username)))
    for transaction in transactions:
        if transaction.payer == user.username and transaction.status == 'successful':
            expenses += transaction.amount
        if transaction.payee == user.username and transaction.status == 'successful':
            income += transaction.amount
    data['expenses'] = expenses
    data['income'] = income
    return response_with(resp.SUCCESS_200, value={'spending': data})
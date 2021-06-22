import os
from flask import Blueprint, json, request, current_app, url_for
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from api.utils import token
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.banks import Banks, BankSchema
from api.utils.database import db

ALLOWED_EXTENSIONS = set(['image/jpeg', 'image/png', 'jpeg', 'jpg', 'image/jpg', 'png'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

bank_routes = Blueprint('bank_routes', __name__)

@bank_routes.route('/', methods=['post'])
def register_bank():
    data = request.get_json()
    if(Banks.find_by_bank(data['bank_name']) is not None):
        return response_with(resp.INVALID_INPUT_422)
    data['password'] = Banks.generate_hash(data['password'])
    bank_schema = BankSchema()
    bank = bank_schema.load(data)
    result = bank_schema.dumps(bank.create())
    return response_with(resp.SUCCESS_200, value={'message': 'please wait for admin verification', 'bank': result})

@bank_routes.route('/<int:bank_id>', methods=['get'])
def get_banks(bank_id):
    fetched = Banks.query.get_or_404(bank_id)
    bank_schema = BankSchema()
    bank = bank_schema.dump(fetched)
    return response_with(resp.SUCCESS_200, value={'bank': bank})

@bank_routes.route('/images/<int:bank_id>', methods = ['post'])
def upsert_author_avatar(bank_id):
    try:
        files = request.files.getlist('files[]')
        get_bank = Banks.query.get_or_404(bank_id)
        for file in files:
            if file.filename == '':
                return response_with(resp.BAD_REQUEST_400)
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            else:
                return response_with(resp.INVALID_INPUT_422)
        get_bank.utility_bills = files[0].filename
        get_bank.certificate_of_incorporation = files[1].filename
        get_bank.bank_statement = files[2].filename
        db.session.add(get_bank)
        db.session.commit()
        bank_schema = BankSchema()
        bank = bank_schema.dump(get_bank)
        return response_with(resp.SUCCESS_200, value={'bank': bank})
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)


import os
from flask import Blueprint, json, request, current_app, url_for
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from api.utils.responses import response_with
from api.utils import responses as resp
from api.utils.database import db
from api.models.board_of_directors import BoardOfDirectors, BODSchema

ALLOWED_EXTENSIONS = set(['image/jpeg', 'image/png', 'jpeg', 'jpg', 'image/jpg', 'png'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

bOd_routes = Blueprint('bOd_routes', __name__)

@bOd_routes.route('/', methods=['post'])
def register_bod():
    data = request.get_json()
    bod_schema = BODSchema()
    bod = bod_schema.load(data)
    result = bod_schema.dumps(bod.create())
    return response_with(resp.SUCCESS_200, value={'BOD': result})

@bOd_routes.route('/images/<int:bod_id>', methods = ['post'])
def upsert_author_avatar(bod_id):
    try:
        files = request.files.getlist('files[]')
        get_bod = BoardOfDirectors.query.get_or_404(bod_id)
        for file in files:
            if file.filename == '':
                return response_with(resp.BAD_REQUEST_400)
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            else:
                return response_with(resp.INVALID_INPUT_422)
        get_bod.document_photo = files[0].filename
        get_bod.passport_photo = files[1].filename
        db.session.add(get_bod)
        db.session.commit()
        bod_schema = BODSchema()
        bod = bod_schema.dump(get_bod)
        return response_with(resp.SUCCESS_200, value={'Director': bod})
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)
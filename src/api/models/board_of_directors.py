from flask_sqlalchemy import model
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

class BoardOfDirectors(db.Model):
    __tablename__ = 'board_of_directors'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('banks.id'))
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phonenumber = db.Column(db.String(120), nullable=False)
    document_id = db.Column(db.String(120), nullable=False)
    document_photo = db.Column(db.String(120))
    passport_photo = db.Column(db.String(120))

    def __init__(self, company_id, first_name, last_name, email, phonenumber, document_id):
        self.company_id = company_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phonenumber = phonenumber
        self.document_id = document_id

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class BODSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = BoardOfDirectors
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    company_id = fields.Integer(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    email = fields.String(required=True)
    phonenumber = fields.String(required=True)
    document_id = fields.String(required=True)
    document_photo = fields.String(dump_only=True)
    passport_photo = fields.String(dump_only=True)
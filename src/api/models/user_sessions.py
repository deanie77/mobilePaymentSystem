from flask_sqlalchemy import model
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

class UserSession(db.Model):
    __tablename__ = 'user_session'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    session_id = db.Column(db.String(120))

    def __init__(self, user_id, session_id):
        self.user_id = user_id
        self.session_id = session_id

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class UserSessionSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = UserSession
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    user_id = fields.Integer(required=True)
    session_id = fields.Integer(required=True)
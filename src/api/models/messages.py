from enum import unique
from flask_sqlalchemy import model
from sqlalchemy.orm import backref
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

class Messages(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(50))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, room_name, sender_id, receiver_id,message):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message = message
        self.room_name = room_name

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_user_one(cls, user_id, other_id):
        return cls.query.filter_by(sender_id = user_id, receiver_id=other_id).first()

    @classmethod
    def find_by_user_two(cls, user_id, other_id):
        return cls.query.filter_by(sender_id=other_id ,receiver_id = user_id).first()

class MessageSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Messages
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    room_name = fields.String(required=True)
    receiver_id = fields.Integer(required=True)
    sender_id = fields.Integer(required=True)
    message = fields.String(required=True)
    created = fields.DateTime(dump_only=True)
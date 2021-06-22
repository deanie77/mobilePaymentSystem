from flask_sqlalchemy import model
from sqlalchemy.orm import query
from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

def same_as(column_name):
    def default_function(context):
        return context.current_parameters.get(column_name)
    return default_function

class Friendships(db.Model):
    __tablename__ = 'friendships'

    user_one = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    user_two = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    action_user = db.Column(db.Integer, default=same_as('user_one'))
    status = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, server_default=db.func.now())
    __table_args__ = (db.UniqueConstraint(user_one, user_two),)

    @staticmethod
    def get_user_friend_list(user_id=None):
        friends = Friendships.query.filter((Friendships.user_one == user_id) | (Friendships.user_two == user_id))
        return friends

    @classmethod
    def find_if_request_exists(cls, user_id, other_id):
        return cls.query.filter_by(user_one = user_id, user_two=other_id).first()

    @classmethod
    def find_if_request_exists_reverse(cls, user_id, other_id):
        return cls.query.filter_by(user_one = other_id, user_two=user_id).first()

    def __init__(self,user_one, user_two, status):
        self.user_one = user_one
        self.user_two = user_two
        self.status = status

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

class FriendshipSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Friendships
        sqla_session = db.session

    user_one = fields.Integer(required=True)
    user_two = fields.Integer(required=True)
    status = fields.Integer(required=True)
    created = fields.DateTime(dump_only=True)
    action_user = fields.Integer(dump_only=True)

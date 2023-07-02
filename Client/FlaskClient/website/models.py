from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin

class Owner(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    hash_password = db.Column(db.String(150))
    message_id = db.Column(db.Integer)
    user_provided_token = db.Column(db.String(150))
    server_provided_token = db.Column(db.String(150))
    hash_server_token = db.Column(db.String(150))
    pub_key = db.Column(db.Text)
    priv_key = db.Column(db.Text)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_owner = db.Column(db.Integer,db.ForeignKey(('owner.id')))
    name = db.Column(db.String(120))
    pub_key= db.Column(db.Text)
    message_id = db.Column(db.Integer)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_receiver = db.Column(db.Integer)
    id_sender = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True),default=func.now())
    delivered = db.Column(db.Boolean)
    message = db.Column(db.Text)
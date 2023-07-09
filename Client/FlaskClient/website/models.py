from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin

class Owner(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    hash_password = db.Column(db.String(150))
    pub_key = db.Column(db.Text)
    priv_key = db.Column(db.Text)
    current_server = db.Column(db.Integer, db.ForeignKey(('server.id')))

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    pub_key= db.Column(db.Text)
    id_owner = db.Column(db.Integer,db.ForeignKey(('owner.id')))
    uuid_contact = db.Column(db.String(150))
    server_id = db.Column(db.Integer, db.ForeignKey(('server.id')))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_receiver = db.Column(db.Integer)
    id_sender = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True),default=func.now())
    message = db.Column(db.Text)
    server_id = db.Column(db.Integer, db.ForeignKey(('server.id')))

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_url = db.Column(db.Text())
    

class isInServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_owner = db.Column(db.Integer,db.ForeignKey(('owner.id')))
    server_id = db.Column(db.Integer, db.ForeignKey(('server.id')))
    hash_server_token = db.Column(db.String(150))
    server_provided_token = db.Column(db.String(150))
    user_provided_token = db.Column(db.String(150))
    uuid = db.Column(db.String(150))
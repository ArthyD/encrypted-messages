from . import db
from sqlalchemy.sql import func

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    pub_key= db.Column(db.Text)
    hash_server_provided_token = db.Column(db.String(150))
    hash_client_provided_token = db.Column(db.String(150))
    server_token = db.Column(db.String(150))
    uuid = db.Column(db.String(300))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid_sender = db.Column(db.String(150), db.ForeignKey('user.uuid'))
    uuid_receiver = db.Column(db.String(150), db.ForeignKey('user.uuid'))
    date = db.Column(db.DateTime(timezone=True),default=func.now())
    delivered = db.Column(db.Boolean)
    message = db.Column(db.Text)
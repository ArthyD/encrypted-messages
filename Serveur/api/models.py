from . import db
from sqlalchemy.sql import func

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    pub_key= db.Column(db.Text)
    hash_token = db.Column(db.String(150))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_sender = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_receiver = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime(timezone=True),default=func.now())
    delivered = db.Column(db.Boolean)
    message = db.Column(db.Text)
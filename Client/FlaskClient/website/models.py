from . import db
from sqlalchemy.sql import func

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    hash_password = db.Column(db.String(150))
    token = db.Column(db.Text)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    pub_key= db.Column(db.Text)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_sender = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_receiver = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime(timezone=True),default=func.now())
    delivered = db.Column(db.Boolean)
    message = db.Column(db.Text)
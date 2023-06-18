from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()
DB_NAME= 'database.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']=os.getenv('APP_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    from .api import api
    app.register_blueprint(api, url_prefix='/')
    create_database(app)

    return app

def create_database(app):
    with app.app_context():
        db.create_all()
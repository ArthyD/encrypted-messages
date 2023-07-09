from flask import Blueprint,render_template, request, flash, redirect, url_for
from .models import Owner, Server, isInServer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, login_required, logout_user
import random, string
from . import db, cryptor
import json
import requests
import os
import secrets


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        user = Owner.query.filter_by(name=name).first()
        if user:
            if check_password_hash(user.hash_password, password):
                flash('Logged in successfully!', category = 'success')
                cryptor.passphrase = password
                cryptor.set_priv_key(user.priv_key)
                cryptor.set_pub_key(user.pub_key)
                login_user(user)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password try again.', category='error')
        else:
            flash("User not known.")
            return redirect(url_for('auth.register'))
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        url = request.form.get('server')
        server = Server.query.filter_by(server_url=url).first()
        if not server:
            server = Server(server_url = url)
            db.session.add(server)
            db.session.commit()
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = Owner.query.filter_by(name=name).first()
        if user:
            flash("User allready registered", category='error')
        elif password1 != password2:
            flash("Passwords do not match", category='error')
        else:
            cryptor.passphrase=password1
            cryptor.generate_keys()
            response = create_account(cryptor,name)
            new_user = Owner(name=name, 
                             hash_password=generate_password_hash(password1, method='scrypt'),  
                             pub_key=cryptor.public_key,
                             priv_key= cryptor.private_key,
                             current_server = server.id)
            newInServer = isInServer(id_owner = new_user.id, 
                                     server_id = server.id,
                                     user_provided_token= response["user_provided_token"],
                                     server_provided_token = response["server_provided_token"],
                                     hash_server_token = generate_password_hash(response["server_token"],"scrypt"),
                                     uuid = response["uuid"])
            db.session.add(new_user)
            db.session.add(newInServer)
            db.session.commit()
            login_user(new_user)
            flash("Account created!", category="success")
            return redirect(url_for('views.home'))
    return render_template("register.html", user=current_user)

def create_account(cryptor,name):
    url = os.getenv('SERVER_URL')
    data = {}
    data["public_key"]=cryptor.public_key.decode()
    data["username"]=name
    user_provided_token=secrets.token_hex(32)
    data["user_provided_token"]=user_provided_token
    data = json.dumps(data)
    response = requests.post(url+f'/create_account',data = data)
    response = json.loads(response.text)
    response["user_provided_token"]= user_provided_token
    return response
            
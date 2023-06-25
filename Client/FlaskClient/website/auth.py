from flask import Blueprint,render_template, request, flash, redirect, url_for
from .models import Owner
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, login_required, logout_user
import random, string
from . import db, cryptor
import json
import requests
import os


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
                cryptor.passphrase=password
                cryptor.load_keys(f'./{user.name}')
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
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = Owner.query.filter_by(name=name).first()
        if user:
            flash("User allready registered", category='error')
        elif password1 != password2:
            flash("Passwords do not match", category='error')
        else:
            token = randomword(100)
            cryptor.passphrase=password1
            cryptor.generate_keys()
            os.makedirs(f'./{name}')
            cryptor.save_priv_key(f'./{name}')
            cryptor.save_pub_key(f'./{name}')  
            id = create_account(cryptor,name,token)
            new_user = Owner(name=name, hash_password=generate_password_hash(password1, method='scrypt'), token=token, message_id=id)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash("Account created!", category="success")
            return redirect(url_for('views.home'))
    return render_template("register.html", user=current_user)

def create_account(cryptor,name,token):
    url = os.getenv('SERVER_URL')
    data = {}
    data["public_key"]=cryptor.public_key.decode()
    data["username"]=name
    data = json.dumps(data)
    response = requests.post(url+f'/create_account',data = data)
    response = json.loads(response.text)
    return response["id"]
            
def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))
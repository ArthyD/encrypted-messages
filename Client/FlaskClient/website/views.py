from flask import Blueprint, jsonify, request, render_template, flash
from . import db
from .models import Owner,Message,Contact
from datetime import datetime
import json
from flask_login import login_required, current_user
from .messenger import MessageReceiver,MessageSender
import os
import requests

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        if 'add_contact' in request.form:
            url = os.getenv('SERVER_URL')
            id = request.form.get('id')
            name = request.form.get('name')
            response = requests.get(url+f'/get_user_key/{id}')
            response = json.loads(response.text)
            if response["id"] == int(id):
                pub_key = response["pub_key"]
                new_contact = Contact(name = name, pub_key=pub_key, message_id = id)
                flash("Contact added", category='success')
                db.session.add(new_contact)
                db.session.commit()
            else:
                flash("Contact not known by server", category = 'error')
    contact_list = Contact.query.all()

    return render_template("home.html", user=current_user, contact_list=contact_list)

@views.route('/message/<contact_id>', methods=['GET', 'POST'])
@login_required
def get_messages(contact_id):
    contact = Contact.query.filter_by(message_id=contact_id).first()
    return render_template("messages.html", user=current_user, contact=contact)
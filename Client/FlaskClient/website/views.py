from flask import Blueprint, jsonify, request, render_template, flash
from . import db, cryptor
from .models import Owner,Message,Contact
from datetime import datetime
import json
from werkzeug.security import check_password_hash
from flask_login import login_required, current_user
from .messenger import MessageReceiver,MessageSender
import os
import requests
from sqlalchemy import or_,and_

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
    if request.method == 'POST':
        if 'load' in request.form:
            receiver = MessageReceiver(current_user.message_id,
                                       cryptor,
                                       current_user.user_provided_token,
                                       current_user.server_provided_token,
                                       current_user.hash_server_token)
            messages = receiver.get_messages()
            print(messages)
            for message in messages:
                new_message = Message(id_receiver=current_user.message_id, 
                                      id_sender=contact.message_id, 
                                      message=message["message"], 
                                      delivered = True)
                db.session.add(new_message)
            db.session.commit()
        elif 'send_message' in request.form:
            try:
                message = request.form.get('message').encode()
                cryptor.set_other_pub_key(contact.pub_key)
                sender = MessageSender(current_user.message_id, 
                                       cryptor,
                                       current_user.user_provided_token,
                                       current_user.server_provided_token,
                                       current_user.hash_server_token)
                sender.send_message(contact.message_id,message)
                new_message = Message(id_receiver=contact.message_id,
                                      id_sender=current_user.message_id,
                                      message=cryptor.own_encrypt(message).decode(),
                                      delivered=False)
                db.session.add(new_message)
                db.session.commit()
            except:
                flash("Error when sending", category='error')
            
    
    list_messages = db.session.query(Message).filter(or_(and_(Message.id_sender==current_user.message_id, Message.id_receiver==contact.message_id),and_(Message.id_sender==contact.message_id, Message.id_receiver==current_user.message_id)))
    messages = []
    for message in list_messages:
        if(message.id_sender == current_user.message_id):
            mess = {}
            mess["sender"] = "me"
            try:
                print("here")
                mess["message"]=cryptor.decrypt_message(message.message.encode()).decode()
            except:
                print("there")
                mess["message"]=message.message
            mess["date"]=message.date
            messages.append(mess)
        elif(message.id_sender == contact.message_id):
            mess = {}
            mess["sender"] = "contact"
            try:
                mess["message"]=cryptor.decrypt_message(message.message.encode()).decode()
            except:
                mess["message"]=message.message
            mess["date"]=message.date
            messages.append(mess)

    return render_template("messages.html", user=current_user, contact=contact, messages=messages)
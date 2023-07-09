from flask import Blueprint, jsonify, request, render_template, flash
from . import db, cryptor
from .models import Owner,Message,Contact, Server, isInServer
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
    server = Server.query.filter_by(id = current_user.current_server).first()
    if request.method == 'POST':
        if 'add_contact' in request.form:
            url = server.server_url
            uuid = request.form.get('uuid')
            name = request.form.get('name')
            response = requests.get(url+f'/get_user_key/{uuid}')
            response = json.loads(response.text)
            if response["uuid"] == uuid:
                pub_key = response["pub_key"]
                new_contact = Contact(name = name, 
                                      id_owner = current_user.id, 
                                      pub_key=pub_key, 
                                      uuid_contact = uuid,
                                      server_id = current_user.current_server)
                flash("Contact added", category='success')
                db.session.add(new_contact)
                db.session.commit()
            else:
                flash("Contact not known by server", category = 'error')
    contact_list = Contact.query.filter_by(id_owner = current_user.id, server_id = current_user.current_server)
    relation = isInServer.query.filter_by(server_id = server.id).first()
    return render_template("home.html", user=current_user, contact_list=contact_list, server = server, isInServer = relation)

@views.route('/message/<contact_uuid>', methods=['GET', 'POST'])
@login_required
def get_messages(contact_uuid):
    contact = Contact.query.filter_by(uuid_contact = contact_uuid).first()
    server = Server.query.filter_by(id = current_user.current_server).first()
    relation = isInServer.query.filter_by(server_id = server.id).first()
    if request.method == 'POST':
        if 'load' in request.form:
            receiver = MessageReceiver(relation.uuid,
                                       cryptor,
                                       relation.user_provided_token,
                                       relation.server_provided_token,
                                       relation.hash_server_token,
                                       server.server_url)
            messages = receiver.get_messages()
            print(messages)
            for message in messages:
                new_message = Message(uuid_receiver=relation.uuid, 
                                      uuid_sender=contact.uuid_contact, 
                                      message=message["message"], 
                                      server_id = server.id)
                db.session.add(new_message)
            db.session.commit()
        elif 'send_message' in request.form:
            try:
                message = request.form.get('message').encode()
                cryptor.set_other_pub_key(contact.pub_key)
                sender = MessageSender(relation.uuid, 
                                       cryptor,
                                       relation.user_provided_token,
                                       relation.server_provided_token,
                                       relation.hash_server_token,
                                       server.server_url)
                sender.send_message(contact.uuid_contact,message)
                new_message = Message(uuid_receiver=contact.uuid_contact,
                                      uuid_sender=relation.uuid,
                                      message=cryptor.own_encrypt(message).decode(),
                                      server_id = server.id)
                db.session.add(new_message)
                db.session.commit()
            except Exception as e:
                print(e)
                flash("Error when sending", category='error')
            
    
    list_messages = db.session.query(Message).filter(or_(and_(Message.uuid_sender==relation.uuid, Message.uuid_receiver==contact.uuid_contact),and_(Message.uuid_sender==contact.uuid_contact, Message.uuid_receiver==relation.uuid)))
    messages = []
    for message in list_messages:
        if(message.uuid_sender == relation.uuid):
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
        elif(message.uuid_sender == contact.uuid_contact):
            mess = {}
            mess["sender"] = "contact"
            try:
                mess["message"]=cryptor.decrypt_message(message.message.encode()).decode()
            except:
                mess["message"]=message.message
            mess["date"]=message.date
            messages.append(mess)

    return render_template("messages.html", user=current_user, contact=contact, messages=messages)
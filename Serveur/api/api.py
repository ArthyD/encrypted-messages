from flask import Blueprint, jsonify, request
from . import db
from .models import User, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import secrets

api = Blueprint('api', __name__)

@api.route('/create_account', methods=['POST'])
def create_user():
    data = json.loads(request.data)
    try:
        print(data['username'])
        print(data['public_key'])
        print(data["user_provided_token"])
        server_provided_token = secrets.token_hex(32)
        server_token = secrets.token_hex(32)
        
        new_user = User(name=data['username'], pub_key=data['public_key'], 
                        hash_server_provided_token = generate_password_hash(server_provided_token, method='scrypt'),
                        hash_client_provided_token = generate_password_hash(data["user_provided_token"], method='scrypt'),
                        server_token = server_token)
        db.session.add(new_user)
        db.session.commit()
        data["server_provided_token"]=server_provided_token
        data["server_token"]=server_token
        data["id"]=new_user.id
        return data
    except:
        print("invalid json")
        return {"response_status":"invalid"}

@api.route('/get_user_key/<id>', methods=['GET'])
def get_user_key(id):
    user = User.query.filter_by(id=id).first()
    data={}
    if user:
        data["id"]=user.id
        data["pub_key"]=user.pub_key
    else:
        data["id"]=-1
        data["pub_key"]=''
    return data

@api.route('/send_message',methods=['POST'])
def send_message():
    data = json.loads(request.data)
    try:
        print(data["sender_id"])
        print(data["receiver_id"])
        print(data["message"])
        print(data["server_provided_token"])
        print(data["user_provided_token"])
        sender = User.query.filter_by(id=int(data["sender_id"])).first()
        receiver = User.query.filter_by(id=int(data["receiver_id"])).first()
        if receiver:
            if check_password_hash(sender.hash_server_provided_token,data["server_provided_token"]) and check_password_hash(sender.hash_client_provided_token,data["user_provided_token"]):
                print("okay")
                new_message = Message(id_sender = int(data["sender_id"]), 
                                    id_receiver = int(data["receiver_id"]), 
                                    message = data["message"],
                                    date= datetime.now(),
                                    delivered = False)
                db.session.add(new_message)
                db.session.commit()
                data={}
                data["id"] = new_message.id
                data["server_token"]=sender.server_token
                return data
            else:
                return {"response_status":"invalid password"}
        else:
            return {"response_status":"invalid"}

    except:
        print("invalid json")
        return {"response_status":"invalid"}


@api.route('/get_my_messages', methods = ['POST'])
def get_list_messages():
    data = json.loads(request.data)
    try:
        print(data["id"])
        print(data["server_provided_token"])
        print(data["user_provided_token"])
        response = {}
        response["messages"]=[]
        
        user = User.query.filter_by(id=int(data["id"])).first()
        if user :
            if check_password_hash(user.hash_server_provided_token,data["server_provided_token"]) and check_password_hash(user.hash_client_provided_token,data["user_provided_token"]):
                messages = Message.query.filter_by(id_receiver = data["id"])
                for message in messages:
                    if(not message.delivered):
                        data_message = {}
                        data_message["sender_id"]= message.id_sender
                        data_message["message"]=message.message
                        data_message["date"]= message.date
                        response["messages"].append(data_message)
                        message.delivered=True
                db.session.commit()
                response["server_token"]= user.server_token
        return response
    except:
        return []

@api.route('get_message/<id>', methods=['GET'])
def get_message(id):
    response = {}
    message = Message.query.filter_by(id=id).first()
    if message:
        response["sender_id"]=message.id_sender
        response["receiver_id"]=message.id_receiver
        response["message"]=message.message
        response["date"]=message.date
        response["delivered"]=message.delivered
    return response
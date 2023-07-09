from flask import Blueprint, jsonify, request
from . import db
from .models import User, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import secrets
import uuid

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
        uuid_user = uuid.uuid4()
        print(uuid_user)
        new_user = User(name=data['username'], 
                        pub_key=data['public_key'], 
                        hash_server_provided_token = generate_password_hash(server_provided_token, method='scrypt'),
                        hash_client_provided_token = generate_password_hash(data["user_provided_token"], method='scrypt'),
                        server_token = server_token,
                        uuid = str(uuid_user))
        db.session.add(new_user)
        db.session.commit()
        data["server_provided_token"]=server_provided_token
        data["server_token"]=server_token
        data["uuid"]=new_user.uuid
        return data
    except Exception as e:
        print(e)
        print("invalid json")
        return {"response_status":"invalid"}

@api.route('/get_user_key/<uuid>', methods=['GET'])
def get_user_key(uuid):
    user = User.query.filter_by(uuid=uuid).first()
    data={}
    if user:
        data["uuid"]=user.uuid
        data["pub_key"]=user.pub_key
    else:
        data["uuid"]=-1
        data["pub_key"]=''
    return data

@api.route('/send_message',methods=['POST'])
def send_message():
    data = json.loads(request.data)
    try:
        print(data["sender_uuid"])
        print(data["receiver_uuid"])
        print(data["message"])
        print(data["server_provided_token"])
        print(data["user_provided_token"])
        sender = User.query.filter_by(uuid=data["sender_uuid"]).first()
        receiver = User.query.filter_by(uuid=data["receiver_uuid"]).first()
        if receiver:
            if check_password_hash(sender.hash_server_provided_token,data["server_provided_token"]) and check_password_hash(sender.hash_client_provided_token,data["user_provided_token"]):
                print("okay")
                new_message = Message(uuid_sender = data["sender_uuid"], 
                                    uuid_receiver = data["receiver_uuid"], 
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
        print(data["uuid"])
        print(data["server_provided_token"])
        print(data["user_provided_token"])
        response = {}
        response["messages"]=[]
        
        user = User.query.filter_by(uuid=data["uuid"]).first()
        if user :
            if check_password_hash(user.hash_server_provided_token,data["server_provided_token"]) and check_password_hash(user.hash_client_provided_token,data["user_provided_token"]):
                messages = Message.query.filter_by(uuid_receiver = data["uuid"])
                for message in messages:
                    if(not message.delivered):
                        data_message = {}
                        data_message["sender_uuid"]= message.uuid_sender
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
        response["sender_uuid"]=message.uuid_sender
        response["receiver_uuid"]=message.uuid_receiver
        response["message"]=message.message
        response["date"]=message.date
        response["delivered"]=message.delivered
    return response
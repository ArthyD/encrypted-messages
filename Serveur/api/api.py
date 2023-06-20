from flask import Blueprint, jsonify, request
from . import db
from .models import User, Message
from datetime import datetime
import json

api = Blueprint('api', __name__)

@api.route('/create_account', methods=['POST'])
def create_user():
    data = json.loads(request.data)
    try:
        print(data['username'])
        print(data['public_key'])
        new_user = User(name=data['username'], pub_key=data['public_key'])
        db.session.add(new_user)
        db.session.commit()
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
        receiver = User.query.filter_by(id=int(data["receiver_id"])).first()
        if receiver:
            print("okay")
            new_message = Message(id_sender = int(data["sender_id"]), 
                                id_receiver = int(data["receiver_id"]), 
                                message = data["message"],
                                date= datetime.now(),
                                delivered = False)
            db.session.add(new_message)
            db.session.commit()
            data["id"] = new_message.id
            return data
        else:
            return {"response_status":"invalid"}

    except:
        print("invalid json")
        return {"response_status":"invalid"}


@api.route('/get_my_messages/<id>', methods = ['GET'])
def get_list_messages(id):
    response = []
    user = User.query.filter_by(id=id).first()
    if user :
        messages = Message.query.filter_by(id_receiver = id)
        for message in messages:
            if(not message.delivered):
                data_message = {}
                data_message["sender_id"]= message.id_sender
                data_message["message"]=message.message
                data_message["date"]= message.date
                response.append(data_message)
                message.delivered=True
        db.session.commit()
    return response

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
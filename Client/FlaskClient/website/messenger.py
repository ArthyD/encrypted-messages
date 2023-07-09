import requests
import os
import json
from werkzeug.security import check_password_hash


class MessageSender:
    def __init__(self,uuid,cryptor, user_provided_token, server_provided_token, hash_server_token,url):
        self.cryptor = cryptor
        self.uuid = uuid
        self.user_provided_token = user_provided_token
        self.sever_provided_token = server_provided_token
        self.hash_server_token = hash_server_token
        self.url = url

    def send_message(self, uuid_receiver,message):
        try:
            user_info = requests.get(self.url+f'/get_user_key/{uuid_receiver}')
            user_info=json.loads(user_info.text)
            self.cryptor.set_other_pub_key(user_info["pub_key"].encode())
            ciphertext = self.cryptor.encrypt_message(message)
            data = {}
            data["sender_uuid"]=self.uuid
            data["receiver_uuid"]=uuid_receiver
            data["message"]=ciphertext.decode()
            data["server_provided_token"] = self.sever_provided_token
            data["user_provided_token"] = self.user_provided_token
            data = json.dumps(data)
            response = requests.post(self.url+f'/send_message', data=data).text
            response = json.loads(response)
            token = response["server_token"]
            if check_password_hash(self.hash_server_token, token):
                print("valid token")
                print(response)
                return response
            else:
                print("invalid token")
                return {}
        except:
            print("Could not send message")

    def send_signature(self, uuid_receiver,message):
        try:
            user_info = requests.get(self.url+f'/get_user_key/{uuid_receiver}')
            user_info=json.loads(user_info.text)
            self.cryptor.set_other_pub_key(user_info["pub_key"].encode())
            ciphertext = self.cryptor.sign_message(message)
            data = {}
            data["sender_uuid"]=self.uuid
            data["receiver_uuid"]=uuid_receiver
            data["message"]=ciphertext.decode()
            data["server_provided_token"] = self.sever_provided_token
            data["user_provided_token"] = self.user_provided_token
            data = json.dumps(data)
            response = requests.post(self.url+f'/send_message', data=data).text
            response = json.loads(response)
            token = response["server_token"]
            if check_password_hash(self.hash_server_token, token):
                print("valid token")
                return response
            else:
                print("invalid token")
                return {}
        except:
            print("Could not send message")

class MessageReceiver:
    def __init__(self,uuid,cryptor, user_provided_token, server_provided_token, hash_server_token, url):
        self.cryptor = cryptor
        self.uuid = uuid
        self.user_provided_token = user_provided_token
        self.sever_provided_token = server_provided_token
        self.hash_server_token = hash_server_token
        self.url = url

    def get_messages(self):
        message_received = []
        try:
            data = {}
            data["uuid"]= self.uuid
            data["server_provided_token"] = self.sever_provided_token
            data["user_provided_token"] = self.user_provided_token
            data = json.dumps(data)
            response = requests.post(self.url+f'/get_my_messages', data=data).text
            response = json.loads(response)
            token = response["server_token"]
            if check_password_hash(self.hash_server_token, token):
                messages= response["messages"]
                for message in messages:
                    message["message"] = message["message"]
                    message_received.append(message)

        except:
            print("Could not get messages")
        return message_received
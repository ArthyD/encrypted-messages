import requests
import os
from .cipher import Cryptor
import json


class MessageSender:
    def __init__(self,id):
        self.cryptor = Cryptor('','','')
        self.cryptor.load_keys(os.getcwd())
        self.id = id
        self.url = os.getenv('SERVER_URL')

    def send_message(self, id_receiver,message):
        try:
            user_info = requests.get(self.url+f'/get_user_key/{id_receiver}')
            user_info=json.loads(user_info.text)
            self.cryptor.set_other_pub_key(user_info["pub_key"].encode())
            ciphertext = self.cryptor.encrypt_message(message)
            data = {}
            data["sender_id"]=self.id
            data["receiver_id"]=id_receiver
            data["message"]=ciphertext.decode()
            data = json.dumps(data)
            response = requests.post(self.url+f'/send_message', data=data)
            return response.text
        except:
            print("Could not send message")

    def send_signature(self, id_receiver,message):
        try:
            user_info = requests.get(self.url+f'/get_user_key/{id_receiver}')
            user_info=json.loads(user_info.text)
            self.cryptor.set_other_pub_key(user_info["pub_key"].encode())
            ciphertext = self.cryptor.sign_message(message)
            data = {}
            data["sender_id"]=self.id
            data["receiver_id"]=id_receiver
            data["message"]=ciphertext.decode()
            data = json.dumps(data)
            response = requests.post(self.url+f'/send_message', data=data)
            return response.text
        except:
            print("Could not send message")
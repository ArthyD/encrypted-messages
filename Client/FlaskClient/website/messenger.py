import requests
import os
import json


class MessageSender:
    def __init__(self,id,cryptor):
        self.cryptor = cryptor
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

class MessageReceiver:
    def __init__(self,id,cryptor):
        self.cryptor = cryptor
        self.id = id
        self.url = os.getenv('SERVER_URL')

    def get_messages(self):
        response = []
        try:
            messages = requests.get(self.url+f'/get_my_messages/{self.id}').text
            messages = json.loads(messages)
            for message in messages:
                message["message"] = message["message"]
                response.append(message)

        except:
            print("Could not get messages")
        return response
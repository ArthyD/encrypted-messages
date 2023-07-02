from Client.FlaskClient.website.messenger import MessageSender, MessageReceiver
from Client.FlaskClient.website.cipher import Cryptor
import requests
import os
import json
import secrets
from werkzeug.security import generate_password_hash

number_test = 2
class TestReceiver:
    def __init__(self):
        self.url = os.getenv('SERVER_URL')
        self.cryptor = Cryptor('','','','password')
        self.cryptor.generate_keys()
        data = {}
        data["public_key"]=self.cryptor.public_key.decode()
        data["username"]="TestReceiver"
        self.user_provided_token=secrets.token_hex(32)
        data["user_provided_token"]=self.user_provided_token
        data = json.dumps(data)
        response = requests.post(self.url+f'/create_account',data = data)
        response = json.loads(response.text)
        self.id_receiver = response["id"]
        self.server_provided_token = response["server_provided_token"]
        self.hash_server_token = generate_password_hash(response["server_token"],"scrypt")
        self.receiver = MessageReceiver(self.id_receiver,self.cryptor, self.user_provided_token, self.server_provided_token, self.hash_server_token)
        
        self.cryptor2 = Cryptor('','','','password')
        self.cryptor2.generate_keys()
        data = {}
        self.user_provided_token2=secrets.token_hex(32)
        data["user_provided_token"]=self.user_provided_token2
        data["public_key"]=self.cryptor2.public_key.decode()
        data["username"]="TestSender"
        data = json.dumps(data)
        response = requests.post(self.url+f'/create_account',data = data)
        response = json.loads(response.text)
        self.id_sender = response["id"]
        self.server_provided_token2 = response["server_provided_token"]
        self.hash_server_token2 = generate_password_hash(response["server_token"],"scrypt")
        self.sender = MessageSender(self.id_sender,self.cryptor, self.user_provided_token2, self.server_provided_token2, self.hash_server_token2)

        self.sender.send_message(self.id_receiver,b'Test1')
        self.sender.send_message(self.id_receiver,b'Test2')
        self.sender.send_message(self.id_receiver,b'Test3')

    def test1(self):
        print(f'[Tester] Test 1/{number_test} : Receive messages')
        try:
            response = self.receiver.get_messages()
            for message in response:
                print(f'Received:{message}')
            print("[*] Test 1 ok")
        except:
            print("[!!] Test 1 ko")

    def test2(self):
        print(f'[Tester] Test 2/{number_test} : Check if queue is empty')
        try:
            response = self.receiver.get_messages()
            if(response == []):
                print("[*] Test 2 ok")
            else: 
                print("[!!] Test 2 ko")
                print(response)
        except:
            print("[!!] Test 2 ko")

if __name__ == '__main__':
    tester = TestReceiver()
    tester.test1()
    tester.test2()
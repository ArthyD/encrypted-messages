from Client.FlaskClient.website.messenger import MessageSender
from Client.FlaskClient.website.cipher import Cryptor
import requests
import os
import json
import secrets
from werkzeug.security import generate_password_hash

number_test = 4
class Test_sender:
    def __init__(self):
        self.url = os.getenv('SERVER_URL')
        self.cryptor = Cryptor('','','','password')
        self.cryptor.generate_keys()
        self.cryptor.save_priv_key(os.getcwd())
        self.cryptor.save_pub_key(os.getcwd())
        data = {}
        data["public_key"]=self.cryptor.public_key.decode()
        data["username"]="TestSender"
        
        self.user_provided_token=secrets.token_hex(32)
        data["user_provided_token"]=self.user_provided_token
        data = json.dumps(data)
        response = requests.post(self.url+f'/create_account',data = data)
        response = json.loads(response.text)
        self.uuid = response["uuid"]
        self.server_provided_token = response["server_provided_token"]
        self.hash_server_token = generate_password_hash(response["server_token"],"scrypt")
        self.sender = MessageSender(self.uuid,self.cryptor, self.user_provided_token, self.server_provided_token, self.hash_server_token, self.url)

    def test1(self):
        print(f'[Tester] Test 1/{number_test} : Send a message')
        try:
            message = b'Hello there'
            self.cryptor_receiver = Cryptor('','','','password')
            self.cryptor_receiver.generate_keys()
            data = {}
            data["public_key"]=self.cryptor_receiver.public_key.decode()
            data["username"]="TestReceiver"
            data["user_provided_token"] = secrets.token_hex(32)
            data = json.dumps(data)
            response = requests.post(self.url+f'/create_account',data = data)
            response = json.loads(response.text)
            self.uuid_receiver = response["uuid"]
            response = self.sender.send_message(self.uuid_receiver,message)
            self.id_message = response["id"]
            print("[*] Test 1 ok")
        except:
            print("[!!] Test 1 ko")

    def test2(self):
        print(f'[Tester] Test 2/{number_test} : Decrypt message')
        try:
            message = b'Hello there'
            response = requests.get(self.url+f'/get_message/{self.id_message}')
            response = json.loads(response.text)
            decipher = self.cryptor_receiver.decrypt_message(response["message"].encode())
            if(message == decipher):
                print("[*] Test 2 ok")
            else:
                print("[!!] Test 2 ko")
        except:
            print("[!!] Test 2 ko")

    def test3(self):
        print(f'[Tester] Test 3/{number_test} : Send a signature')
        try:
            message = b'Signature'
            response = self.sender.send_signature(self.uuid_receiver,message)
            self.id_message = response["id"]
            print("[*] Test 3 ok")
        except:
            print("[!!] Test 3 ko")

    def test4(self):
        print(f'[Tester] Test 4/{number_test} : Verify a signature')
        try:
            message = b'Signature'
            response = requests.get(self.url+f'/get_message/{self.id_message}')
            response = json.loads(response.text)
            self.cryptor_receiver.set_other_pub_key(self.cryptor.public_key)
            self.cryptor_receiver.decrypt_signature(response["message"].encode(),message)
            print("[*] Test 4 ok")
        except:
            print("[!!] Test 4 ko")


if __name__ == '__main__':
    tester = Test_sender()
    tester.test1()
    tester.test2()
    tester.test3()
    tester.test4()
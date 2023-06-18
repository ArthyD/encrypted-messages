from Client.messenger import MessageSender, MessageReceiver
from Client.cipher import Cryptor
import requests
import os
import json

number_test = 2
class TestReceiver:
    def __init__(self):
        self.url = os.getenv('SERVER_URL')
        self.cryptor = Cryptor('','','')
        self.cryptor.generate_keys()
        data = {}
        data["public_key"]=self.cryptor.public_key.decode()
        data["username"]="TestReceiver"
        data = json.dumps(data)
        response = requests.post(self.url+f'/create_account',data = data)
        response = json.loads(response.text)
        self.id_receiver = response["id"]
        self.receiver = MessageReceiver(self.id_receiver,self.cryptor)
        
        self.cryptor2 = Cryptor('','','')
        self.cryptor2.generate_keys()
        data = {}
        data["public_key"]=self.cryptor2.public_key.decode()
        data["username"]="TestSender"
        data = json.dumps(data)
        response = requests.post(self.url+f'/create_account',data = data)
        response = json.loads(response.text)
        self.id_sender = response["id"]
        self.sender = MessageSender(self.id_sender,self.cryptor)

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
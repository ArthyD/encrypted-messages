
from Client.FlaskClient.website.cipher import Cryptor

number_test = 6
class Test_Cipher:
    def __init__(self):
        self.cryptor2 = Cryptor('','','','test')
        self.cryptor1 = Cryptor('','','','test')
    
    def test1(self):
        print(f'[Tester] Test 1/{number_test} : generate keys')  
        self.cryptor1.generate_keys()
        self.cryptor2.generate_keys()
        if(self.cryptor1.public_key != '' and self.cryptor1.public_key != '' and self.cryptor2.private_key != '' and self.cryptor2.public_key != ''):
            print("[*] Test 1 ok")
        else:
            print("[!!] Test 1 ko")  

    def test2(self):
        print(f'[Tester] Test 2/{number_test} : set other key')
        self.cryptor1.set_other_pub_key(self.cryptor2.public_key)
        self.cryptor2.set_other_pub_key(self.cryptor1.public_key)
        if(self.cryptor1.other_pub_key == self.cryptor2.public_key and self.cryptor2.other_pub_key == self.cryptor1.public_key):
            print("[*] Test 2 ok")
        else:
            print("[!!] Test 2 ko")

    def test3(self):
        print(f'[Tester] Test 3/{number_test} encrypt message from A and decrypt from B')
        message = b'Hello there'
        ciphertext = self.cryptor1.encrypt_message(message)
        decipher = self.cryptor2.decrypt_message(ciphertext)
        if(decipher == message):
            print("[*] Test 3 ok")
        else:
            print("[!!] Test 3 ko")

    def test4(self):
        print(f'[Tester] Test 4/{number_test} signature from A and check from B')
        message = b'General Kenobi'
        ciphertext = self.cryptor1.sign_message(message)
        if(self.cryptor2.decrypt_signature(ciphertext,message)):
            print("[*] Test 4 ok")
        else:
            print("[!!] Test 4 ko")

    def test5(self):
        print(f'[Tester] Test 5/{number_test} save keys')
        try:
            self.cryptor1.save_priv_key('./')
            self.cryptor1.save_pub_key('./')
            print("[*] Test 5 ok")
        except:
            print("[!!] Test 5 ko")
        
    def test6(self):
        print(f'[Tester] Test 6/{number_test} load keys')
        message=b'Is loading working ?'
        encrypted = self.cryptor1.encrypt_message(message)
        self.cryptor1.load_keys('.')
        encrypted_after = self.cryptor1.encrypt_message(message)
        if self.cryptor2.decrypt_message(encrypted) != self.cryptor2.decrypt_message(encrypted_after):
            print("[!!] Test 6 ko")
        else:
            print("[*] Test 6 ok")



if __name__ == '__main__':
    test = Test_Cipher()
    test.test1()
    test.test2()
    test.test3()
    test.test4()
    test.test5()
    test.test6()
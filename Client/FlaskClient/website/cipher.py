from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES,PKCS1_OAEP
from Cryptodome.Random import get_random_bytes
from Cryptodome.Signature import pkcs1_15
from Cryptodome.Hash import SHA256
from io import BytesIO
import base64
import zlib

class Cryptor:
    def __init__(self,public_key,private_key,other_pub_key):
        self.public_key = public_key
        self.private_key = private_key
        self.other_pub_key = other_pub_key

    def generate_keys(self):
        new_key = RSA.generate(2048)
        self.private_key = new_key.exportKey()
        self.public_key = new_key.publickey().exportKey()

    def save_priv_key(self,path):
        with open(path+'/key.pri','wb') as f:
            f.write(self.private_key)

    def save_pub_key(self, path):
        with open(path+'/key.pub','wb') as f:
            f.write(self.public_key)

    def load_keys(self, path):
        with open(path+'/key.pri') as f:
            self.private_key = f.read()
        with open(path+'/key.pub') as f:
            self.public_key = f.read()

    def set_other_pub_key(self,other_pub_key):
        self.other_pub_key = other_pub_key

    def get_rsa_cipher(self,keytype):
        if keytype == 'private':
            rsakey = RSA.importKey(self.private_key)
        elif keytype == 'public':
            rsakey = RSA.importKey(self.public_key)
        elif keytype == 'other':
            rsakey = RSA.importKey(self.other_pub_key)
        else:
            raise Exception("Unknown type of key")
        return (PKCS1_OAEP.new(rsakey), rsakey.size_in_bytes())
    
    def encrypt_message(self, plaintext):
        compressed_text = zlib.compress(plaintext)
        session_key = get_random_bytes(16)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(compressed_text)

        cipher_rsa, _ = self.get_rsa_cipher('other')
        encrypted_session_key = cipher_rsa.encrypt(session_key)

        msg_payload = encrypted_session_key +cipher_aes.nonce + tag + ciphertext
        encrypted = base64.encodebytes(msg_payload)
        return encrypted
    
    def sign_message(self, plaintext):
        h = SHA256.new(plaintext)
        signature = pkcs1_15.new(RSA.importKey(self.private_key)).sign(h)
        encrypted = base64.encodebytes(signature)
        return encrypted
    
    def decrypt_message(self, cipher):
        encrypted_bytes = BytesIO(base64.decodebytes(cipher))
        cipher_rsa, key_size_in_bytes = self.get_rsa_cipher('private')

        encrypted_session_key = encrypted_bytes.read(key_size_in_bytes)
        nonce = encrypted_bytes.read(16)
        tag = encrypted_bytes.read(16)
        ciphertext = encrypted_bytes.read()

        session_key = cipher_rsa.decrypt(encrypted_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        decrypted = cipher_aes.decrypt_and_verify(ciphertext, tag)

        plaintext = zlib.decompress(decrypted)

        return plaintext
    
    def decrypt_signature(self, signature, plaintext):
        h = SHA256.new(plaintext)
        try:
            encrypted_bytes = BytesIO(base64.decodebytes(signature))
            ciphertext = encrypted_bytes.read()
            pkcs1_15.new(RSA.importKey(self.other_pub_key)).verify(h, ciphertext)
            print("[*] Signature ok")
            return True
        except ValueError:
            print("[!!] Signature not valid")
            return False

        





    
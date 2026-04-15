import socket
import threading
import json
from modular_operations import generate_keypair, encrypt, decrypt, get_hash

class Client:
    def __init__(self, server_ip: str, port: int, username: str) -> None:
        self.server_ip = server_ip
        self.port = port
        self.username = username

    def init_connection(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.server_ip, self.port))
        except Exception as e:
            print("[client]: could not connect to server: ", e)
            return

        self.s.send(self.username.encode())

        # create key pairs
        self.public_key, self.private_key = generate_keypair()

        # exchange public keys
        self.s.send(json.dumps(self.public_key).encode())

        # receive the encrypted secret key
        server_key_data = self.s.recv(4096).decode()
        self.server_public_key = json.loads(server_key_data)

        message_handler = threading.Thread(target=self.read_handler,args=())
        message_handler.start()
        input_handler = threading.Thread(target=self.write_handler,args=())
        input_handler.start()

    def read_handler(self):
        while True:
            message = self.s.recv(4096).decode()

            try:
                data_packet = json.loads(message)

                decrypted_text = decrypt(self.private_key, data_packet["data"])

                if get_hash(decrypted_text) == data_packet["hash"]:
                    message = decrypted_text
                else:
                    message = "[ Integrity Error ]: Повідомлення було підроблено!"
            except:
                pass

            print(message)

    def write_handler(self):
        while True:
            message = input()

            # encrypt message with the secrete key
            msg_hash = get_hash(message)
            encrypted_msg = encrypt(self.server_public_key, message)

            packet = json.dumps({
                "hash": msg_hash,
                "data": encrypted_msg
            })

            self.s.send(packet.encode())

if __name__ == "__main__":
    cl = Client("127.0.0.1", 9001, "b_g")
    cl.init_connection()

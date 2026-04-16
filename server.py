import socket
import threading
import json
from modular_operations import generate_keypair, encrypt, decrypt, get_hash

class Server:

    def __init__(self, port: int) -> None:
        self.host = '127.0.0.1'
        self.port = port
        self.clients = []
        self.username_lookup = {}
        self.client_keys = {}
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def start(self):
        self.s.bind((self.host, self.port))
        self.s.listen(100)

        # generate keys ...
        self.public_key, self.private_key = generate_keypair()
        print(f"[Сервер запущено] Згенеровано RSA ключі.")

        while True:
            c, addr = self.s.accept()
            username = c.recv(1024).decode()
            print(f"{username} tries to connect")
            self.broadcast(f'new person has joined: {username}')
            self.username_lookup[c] = username
            self.clients.append(c)

            # send public key to the client

            client_key_data = c.recv(4096).decode()
            self.client_keys[c] = json.loads(client_key_data)
            c.send(json.dumps(self.public_key).encode())

            threading.Thread(target=self.handle_client,args=(c,addr,)).start()

    def broadcast(self, msg: str):
        for client in self.clients:

            # encrypt the message
            client_pub_key = self.client_keys.get(client)
            if not client_pub_key:
                continue

            msg_hash = get_hash(msg)
            encrypted_msg = encrypt(client_pub_key, msg)
            packet = json.dumps({
                "hash": msg_hash,
                "data": encrypted_msg
            })
            try:
                client.send(packet.encode())
            except:
                pass

    def handle_client(self, c: socket, addr):
        username = self.username_lookup.get(c, "Unknown")
        while True:
            try:
                raw_data = c.recv(4096).decode()
                if not raw_data:
                    break

                packet = json.loads(raw_data)
                received_hash = packet["hash"]
                encrypted_data = packet["data"]

                decrypted_msg = decrypt(self.private_key, encrypted_data)

                if get_hash(decrypted_msg) == received_hash:
                    final_msg = f"{username}: {decrypted_msg}"
                    print(final_msg)

                    for client in self.clients:
                        if client != c:
                            client_pub_key = self.client_keys[client]
                            f_hash = get_hash(final_msg)
                            f_enc = encrypt(client_pub_key, final_msg)

                            f_packet = json.dumps({
                                "hash": f_hash,
                                "data": f_enc
                            })
                            client.send(f_packet.encode())
                else:
                    print(f"[УВАГА] Повідомлення від {username} було пошкоджено!")

            except Exception as e:
                print(f"[Відключення] {username} покинув чат.")
                self.clients.remove(c)
                del self.username_lookup[c]
                del self.client_keys[c]
                c.close()
                break

if __name__ == "__main__":
    s = Server(9001)
    s.start()

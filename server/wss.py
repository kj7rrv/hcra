import os
import base64
import hcapi
import threading
import logging
import random
import time
import shutil
import tempfile
import queue
from websocket_server import WebsocketServer

def cycle():
    try:
        changed = hcapi.get_img()
    except Exception as e:
        #server.send_message_to_all('err%noconn%Server failed to capture screenshot')
        for client in clients.values():
            client.send('err%noconn%Server failed to capture screenshot', 'ERR')
        time.sleep(3)
        return

    for i in changed:
        threading.Thread(target=do_img, args=(i,)).start()

    for client in clients.values():
        client.ack()


class Client:
    def __init__(self, client, server):
        self.client = client
        self.server = server
        self.queue = queue.Queue()
        self.items = {}
        self.lock = threading.Lock()
        self.good = True
    
    def send(self, item, name):
        with self.lock:
            self.items[name] = item

    def ack(self):
        with self.lock:
            try:
                self.server.send_message(self.client, 'ack')
                self.good = False
            except BrokenPipeError:
                pass

    def cycle(self):
        with self.lock:
            try:
                while not self.good:
                    pass
                for name, item in list(self.items.items()):
                    if not self.good:
                        break
                    self.server.send_message(self.client, item)
                    del self.items[name]
            except BrokenPipeError:
                pass

    def run(self):
        while True:
            self.cycle()
clients = {}

def do_img(imgname):
    for client in clients.values():
        client.send(img(imgname), imgname)


def img(imgname):
    with open(f'pieces/{imgname}.jpg', 'rb') as f:
        img = f.read()

    response = f'pic%{imgname}%data:imgage/jpeg;base64,{base64.b64encode(img).decode("utf-8")}'

    return response

def new_client(client, server):
    if clients:
        server.send_message(client, 'err%*inuse%Server already in use')
        client['handler'].send_text("", opcode=0x8)
        return

    clients[client['id']] = Client(client, server)
    try:
        imgname = hcapi.get_full_img()
    except Exception as e:
        server.send_message(client, 'err%noconn%Server failed to capture screenshot')
        return

    clients[client['id']] = Client(client, server)

    with open(imgname, 'rb') as f:
        img = f.read()
    os.unlink(imgname)
    server.send_message(client, f'pic%0x0%data:imgage/jpeg;base64,{base64.b64encode(img).decode("utf-8")}')
    clients[client['id']] = Client(client, server)
    clients[client['id']].ack()
    threading.Thread(target=clients[client['id']].run).start()

def do_touch(client, server, message):
    action = message.split(' ', 1)[0]
    if action == 'ack':
        clients[client['id']].good = True
    else:
        _, password, x, y, w, is_long = message.split(' ')
        if password == 'password':
            x, y, w, is_long = int(x), int(y), int(w), bool(is_long)
            hcapi.touch(x, y, w, is_long)
        else:
            clients[client['id']].send(f'badpass', 'BADPASS')

def client_left(client, server):
    clients[client['id']].good = False
    del clients[client['id']]

def do_cycles():
    while True:
        if clients:
            cycle()
            time.sleep(0.4)
        else:
            time.sleep(1)

tmp = tempfile.mkdtemp(prefix="HCRA-")
try:
    shutil.copy('crops.json', tmp)
    os.chdir(tmp)
    os.mkdir('pieces')
    server = WebsocketServer(1234, host='0.0.0.0', loglevel=logging.INFO)
    threading.Thread(target=do_cycles).start()
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(do_touch)
    server.set_fn_client_left(client_left)
    server.run_forever()
finally:
    os.chdir('/')
    shutil.rmtree(tmp)
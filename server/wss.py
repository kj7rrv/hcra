import argon2
import asyncio
import base64
import imgproc
import importlib
import os
import parse_config
import random
import requests
import secrets
import shutil
import sys
import tempfile
import threading
import time
import tornado.web, tornado.websocket, tornado.ioloop

try:
    conf = sys.argv[1]
except IndexError:
    conf = 'conf.txt'

with open(conf) as f:
    config_data = parse_config.load(f)

imgproc.backend = importlib.import_module(f'backends.{config_data["backend"]}')
imgproc.backend.config = config_data
imgproc.config = config_data

ph = argon2.PasswordHasher()

client = None


token = secrets.token_urlsafe(64)


class DisconnectError(BaseException):
    pass


class Client:
    def __init__(self, conn):
        global client
        if client is not None:
            raise DisconnectError('err%*inuse%Server already in use')

        client = self
        self.conn = conn
        self.items = {}
        self.lock = threading.Lock()
        self.good = True

    def send(self, item, name):
        with self.lock:
            self.items[name] = item

    def ack(self):
        with self.lock:
            self.good = False

    def get_item_to_send(self):
        with self.lock:
            if self.items:
                name, content = list(self.items.items())[0]
                del self.items[name]
                return name, content
            elif not self.good:
                return 'ack', 'ack'
            else:
                return None, None



class HCRAServer(tornado.websocket.WebSocketHandler):
    def open(self):
        self.has_auth = False

    def on_close(self):
        global client
        if client is self.client:
            self.client.good = None
            client = None
        self.is_open = False

    def on_message(self, message):
        action = message.split(' ', 1)[0]
        if not self.has_auth:
            print(message)
            print(action)
            print(action != 'pass')
            if action != 'pass':
                self.write_message('err%*mustauth%Authentication required')
                self.close()
                return

            try:
                ph.verify(config_data['password_argon2'], message.split(' ', 1)[1])
            except argon2.exceptions.VerifyMismatchError:
                self.write_message(f'err%*badpass%Incorrect password')
                self.close()
                return

            try:
                self.client = Client(self)
            except DisconnectError as e:
                self.write_message(str(e))
                return

            try:
                imgname = imgproc.get_full_img()
            except Exception as e:
                self.write_message('err%noconn%Server failed to capture screenshot')
                return

            with open(imgname, 'rb') as f:
                img = f.read()
            os.unlink(imgname)
            self.write_message(f'pic%0x0%data:image/jpeg;base64,{base64.b64encode(img).decode("utf-8")}')
            self.is_open = True
            self.client.ack()

            self.has_auth = True
        else:
            if action == 'ack':
                self.client.good = True
            else:
                print(message)
                _, x, y, w, is_long = message.split(' ')
                x, y, w, is_long = int(x), int(y), int(w), is_long == 'true'
                imgproc.touch(x, y, w, is_long)

    def check_origin(self, origin):
        return True

def cycle():
    try:
        changed = imgproc.get_split_imgs()
    except Exception as e:
        if client is not None:
            client.send('err%noconn%Server failed to capture screenshot', 'ERR')
        time.sleep(3)
        return

    threads = []
    for i in changed:
        thread = threading.Thread(target=do_img, args=(i,))
        threads.append(thread)
        thread.start()

    if client is not None:
        client.ack()


def do_img(imgname):
    if client is not None:
        client.send(img(imgname), imgname)


def img(imgname):
    with open(f'pieces/{imgname}.jpg', 'rb') as f:
        img = f.read()

    response = f'pic%{imgname}%data:image/jpeg;base64,{base64.b64encode(img).decode("utf-8")}'

    return response


def do_cycles():
    while True:
        if client is not None:
            cycle()
            time.sleep(0.4)
        else:
            time.sleep(1)




class Cycler(tornado.web.RequestHandler):
    def get(self):
        if client is not None:
            name, item = client.get_item_to_send()
            if item is not None:
                client.conn.write_message(item)
        self.write('OK')


def get_token():
    while True:
        requests.get('http://localhost:1234/' + token)


tmp = tempfile.mkdtemp(prefix="HCRA-")
try:
    shutil.copy('crops.json', tmp)
    os.chdir(tmp)
    os.mkdir('pieces')

    threading.Thread(target=do_cycles).start()

    application = tornado.web.Application([
        (r"/", HCRAServer),
        ('/' + token, Cycler),
    ])
    application.listen(1234)
    threading.Thread(target=get_token).start()
    tornado.ioloop.IOLoop.current().start()
finally:
    os.chdir('/')
    shutil.rmtree(tmp)

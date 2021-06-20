# Select backend - 'port8080' uses HamClock's port 8080 service; 'x11' uses an
# X11 server (typically Xvfb) (make sure DISPLAY is set correctly!)

# use_backend = 'x11'
# use_backend = 'port8080'


import os
import base64
import threading
import random
import time
import shutil
import tempfile
import tornado.web, tornado.websocket, tornado.ioloop
import imgproc as hcapi
import argon2
import asyncio
import importlib
import parse_config 


with open('conf.txt') as f:
    config_data = parse_config.load(f)

hcapi.backend = importlib.import_module(f'backends.{config_data["backend"]}')
hcapi.backend.config = config_data
hcapi.config = config_data

ph = argon2.PasswordHasher()

client = None


class HCRAServer(tornado.websocket.WebSocketHandler):
    def open(self):
        global client
        if client is not None:
            self.write_message('err%*inuse%Server already in use')
            self.close()
        else:
            client = self
            self.items = {}
            self.lock = threading.Lock()
            self.good = True
            try:
                imgname = hcapi.get_full_img()
            except Exception as e:
                self.write_message('err%noconn%Server failed to capture screenshot')
                return

            with open(imgname, 'rb') as f:
                img = f.read()
            os.unlink(imgname)
            self.write_message(f'pic%0x0%data:imgage/jpeg;base64,{base64.b64encode(img).decode("utf-8")}')
            self.ack()
            loop = asyncio.new_event_loop()
            threading.Thread(target=self.run, args=(loop,)).start()

    def send(self, item, name):
        with self.lock:
            self.items[name] = item

    def ack(self):
        with self.lock:
            self.items['ack'] = 'ack'

    async def cycle(self):
        with self.lock:
            while not self.good:
                pass
            for name, item in list(self.items.items()):
                if not self.good:
                    break
                self.write_message(item)
                del self.items[name]
                if item == 'ack':
                    self.good = False

    def run(self, loop):
        asyncio.set_event_loop(loop)
        while True:
            if client is not self:
                break
            loop.run_until_complete(self.cycle())

    def on_close(self):
        global client
        if client is self:
            self.good = None
            client = None

    def on_message(self, message):
        action = message.split(' ', 1)[0]
        if action == 'ack':
            self.good = True
        else:
            _, password, x, y, w, is_long = message.split(' ')
            try:
                ph.verify(config_data['password_argon2'], password)
                x, y, w, is_long = int(x), int(y), int(w), is_long == 'true'
                hcapi.touch(x, y, w, is_long)
            except argon2.exceptions.VerifyMismatchError:
                self.send(f'err%*badpass%Incorrect password', 'BADPASS')
                self.close()

    def check_origin(self, origin):
        return True


def cycle():
    try:
        changed = hcapi.get_split_imgs()
    except Exception as e:
        if client is not None:
            client.send('err%noconn%Server failed to capture screenshot', 'ERR')
        time.sleep(3)
        return

    for i in changed:
        threading.Thread(target=do_img, args=(i,)).start()

    if client is not None:
        client.ack()


def do_img(imgname):
    if client is not None:
        client.send(img(imgname), imgname)


def img(imgname):
    with open(f'pieces/{imgname}.jpg', 'rb') as f:
        img = f.read()

    response = f'pic%{imgname}%data:imgage/jpeg;base64,{base64.b64encode(img).decode("utf-8")}'

    return response


def do_cycles():
    while True:
        if client is not None:
            cycle()
            time.sleep(0.4)
        else:
            time.sleep(1)


tmp = tempfile.mkdtemp(prefix="HCRA-")
try:
    shutil.copy('crops.json', tmp)
    os.chdir(tmp)
    os.mkdir('pieces')

    threading.Thread(target=do_cycles).start()

    application = tornado.web.Application([
        (r"/", HCRAServer),
    ])
    application.listen(1234)
    tornado.ioloop.IOLoop.current().start()
finally:
    os.chdir('/')
    shutil.rmtree(tmp)

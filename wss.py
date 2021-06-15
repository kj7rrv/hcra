import os
import base64
import hcapi
import threading
import logging
import random
import time
import shutil
import tempfile
from websocket_server import WebsocketServer

def cycle():
    try:
        changed = hcapi.get_img()
    except ImportError as e:
        server.send_message_to_all('err%noconn%Server failed to capture screenshot')
        time.sleep(3)
        return

    for i in changed:
        threading.Thread(target=do_img, args=(i,)).start()      


def do_img(imgname):
    server.send_message_to_all(img(imgname))


def img(imgname):
    with open(f'pieces/{imgname}.jpg', 'rb') as f:
        img = f.read()

    response = f'pic%{imgname}%data:imgage/jpeg;base64,{base64.b64encode(img).decode("utf-8")}'

    return response

def new_client(client, server):
    print('got client')
    try:
        imgname = hcapi.get_full_img()
    except Exception as e:
        server.send_message(client, 'err%noconn%Server failed to capture screenshot')
        return

    with open(imgname, 'rb') as f:
        img = f.read()
    os.unlink(imgname)
    server.send_message(client, f'pic%0x0%data:imgage/jpeg;base64,{base64.b64encode(img).decode("utf-8")}')

def do_touch(client, server, message):
    password, x, y, w = message.split(' ')
    if password == 'password':
        x, y, w = int(x), int(y), int(w)
        hcapi.touch(x, y, w)
    else:
        server.send_message(client, f'badpass')

def do_cycles():
    while True:
        cycle()

tmp = tempfile.mkdtemp(prefix="HCRA-")
try:
    shutil.copy('crops.json', tmp)
    os.chdir(tmp)
    os.mkdir('pieces')
    server = WebsocketServer(1234, host='0.0.0.0', loglevel=logging.INFO)
    threading.Thread(target=do_cycles).start()
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(do_touch)
    server.run_forever()
finally:
    os.chdir('/')
    shutil.rmtree(tmp)

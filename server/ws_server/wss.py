# Copyright (C) 2021 Samuel L Sloniker KJ7RRV

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argon2
import base64
import imgproc
import importlib
import logging
import os
import parse_config
import sys
import threading
import time
from websocket_server import WebsocketServer

try:
    conf = sys.argv[1]
except IndexError:
    conf = 'conf.txt'

with open(conf) as f:
    config_data = parse_config.load(f)

backend = importlib.import_module(f'backends.{config_data["backend"]}')
backend.config = config_data
imgproc.config = config_data
imgproc.backend = backend

ph = argon2.PasswordHasher()

client = None


class DisconnectError(BaseException):
    pass


class Client:
    def __init__(self, server, client_):
        global client
        if client is not None:
            raise DisconnectError('err%*inuse%Server already in use')

        client = self
        self.server = server
        self.client = client_
        self.has_auth = False
        self.ready_for_msgs = False
        self.acked = True
        self.version = None
        self.next_msg = None

    def close(self):
        global client
        self.ready_for_msgs = False
        client = None
        imgproc.backend.disconnect()

    def do_send(self):
        if self.next_msg is not None and self.ready_for_msgs and self.acked:
            msg = self.next_msg
            self.next_msg = None
            self.server.send_message(self.client, msg)
            self.server.send_message(self.client, 'ack')
            self.acked = False

    def got_ack(self):
            self.acked = True
            self.do_send()


def on_left(client_, server):
    global client
    if client_ != client.client:
        return
    
    client.close()


def on_message(client_, server, message):
    global client
    if client_ != client.client:
        return

    action = message.split(' ', 1)[0]
    if client.version is None:
        if action == 'maxver':
            client.version = min(int(message.split(' ', 1)[1]), 1)
            server.send_message(client_, f'ver%{client.version}')
        else:
            server.send_message(client_, 'err%*mustmaxver%Client must send version')
            client_['handler'].send_text("", opcode=0x8)
            return
    elif not client.has_auth:
        if action != 'pass':
            server.send_message(client_, 'err%*mustauth%Authentication required')
            client_['handler'].send_text("", opcode=0x8)
            return

        try:
            ph.verify(config_data['password_argon2'], message.split(' ', 1)[1])
        except argon2.exceptions.VerifyMismatchError:
            server.send_message(client_, f'err%*badpass%Incorrect password')
            client_['handler'].send_text("", opcode=0x8)
            return

        client.has_auth = True
        
        imgproc.backend.connect()

        client.ready_for_msgs = True
        client.do_send()

    else:
        if action == 'ack':
            client.got_ack()
        else:
            _, x, y, w, is_long = message.split(' ')
            x, y, w, is_long = int(x), int(y), int(w), is_long == 'true'
            imgproc.touch(x, y, w, is_long)


def on_connect(client_, server):
    try:
        client = Client(server, client_)
    except DisconnectError as e:
        server.send_message(client_, str(e))
        client_['handler'].send_text("", opcode=0x8)
        return


def get_img_msg():
    try:
        img = imgproc.get_img()
    except Exception as e:
        return 'err%noconn%Server failed to capture screenshot'

    with open(img, 'rb') as f:
        img_data = f.read()
    
    os.unlink(img)

    return f'pic%0x0%data:image/webp;base64,{base64.b64encode(img_data).decode("utf-8")}'

def cycle():
    if client is not None:
        msg = get_img_msg()
        try:
            client.next_msg = msg
            client.do_send()
        except AttributeError as e:
            if "'NoneType' object has no attribute" in str(e):
                return
            else:
                raise e

def do_cycles():
    while True:
        cycle()
        time.sleep(0.8)


threading.Thread(target=do_cycles).start()
server = WebsocketServer(int(config_data['port']), host='0.0.0.0', loglevel=logging.INFO)
server.set_fn_new_client(on_connect)
server.set_fn_message_received(on_message)
server.set_fn_client_left(on_left)
server.run_forever()

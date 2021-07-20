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

import os
import subprocess
import threading
import time


def _long_touch(x, y):
    os.environ['DISPLAY'] = config['display']
    subprocess.run(['xdotool', 'mousemove', str(x), str(y), 'mousedown', '1'])
    time.sleep(2)
    subprocess.run(['xdotool', 'mouseup', '1'])


def get_img():
    os.environ['DISPLAY'] = config['display']
    xwd = subprocess.Popen(['xwd', '-root', '-silent'], stdout=subprocess.PIPE)
    convert = subprocess.Popen(['convert', 'xwd:-', 'bmp:img.bmp'], stdin=xwd.stdout)
    convert.wait()
    return 'img.bmp'


def touch(x, y, is_long):
    os.environ['DISPLAY'] = config['display']
    if is_long:
        threading.Thread(target=_long_touch, args=(x, y,)).start()
    else:
        subprocess.run(['xdotool', 'mousemove', str(x), str(y), 'click', '1'])


def connect():
    global _hamclock
    os.environ['DISPLAY'] = config['display']
    _hamclock = subprocess.Popen(config['hamclock_bin'])


def disconnect():
    _hamclock.terminate()
    _hamclock.wait()

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

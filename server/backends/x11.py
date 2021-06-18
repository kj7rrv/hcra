import os
import threading
import time


def _long_touch(x, y):
    os.system(f'xdotool mousemove {x} {y} mousedown 1')
    time.sleep(2)
    os.system(f'xdotool mouseup 1')


def get_img():
    os.system('xwd -root -silent | convert xwd:- img.bmp')
    return 'img.bmp'


def touch(x, y, is_long):
    if is_long:
        threading.Thread(target=_long_touch, args=(x, y,)).start()
    else:
        os.system(f'xdotool mousemove {x} {y} click 1')

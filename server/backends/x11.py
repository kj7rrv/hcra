import os
import requests
import threading
import json
import time

def get_img():
    os.system('xwd -root -silent | convert xwd:- img.bmp')
        
    with open('crops.json') as f:
        crops = json.load(f)

    threads = []
    for crop in crops:
        threads.append(threading.Thread(target=os.system, args=(f'convert img.bmp -crop {crop} pieces/{crop.split("+", 1)[1].replace("+", "x")}.jpg',)))
        threads[-1].start()
    for thread in threads:
        thread.join()

    os.system("md5sum -c oldlist 2>/dev/null | grep FAILED > newlist")
    changed = []
    with open('newlist') as f:
        lines = f.readlines()
        for line in lines:
            changed.append(line.split(": ")[0].split('.')[0].split('/')[1])
    os.system("md5sum pieces/* > oldlist")
    return changed

def get_full_img():
    os.system('xwd -root -silent | convert xwd:- full.jpg')
    return 'full.jpg'

def touch(x, y, w, is_long):
    x = round(800 * x / w)
    y = round(800 * y / w)
    if is_long:
        os.system(f'xdotool mousemove {x} {y} mousedown 1')
        time.sleep(2)
        os.system(f'xdotool mouseup 1')
    else:
        os.system(f'xdotool mousemove {x} {y} click 1')

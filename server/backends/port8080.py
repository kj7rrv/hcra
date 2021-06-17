import os
import requests
import threading
import json

def get_img():
    raw_img = requests.get('http://localhost:8080/get_capture.bmp').content

    with open('full_img.bmp', 'wb+') as f:
        f.write(raw_img)

    os.system('convert full_img.bmp -resize 800x480 img.bmp')
        
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
    raw_img = requests.get('http://localhost:8080/get_capture.bmp').content

    with open('full_full.bmp', 'wb+') as f:
        f.write(raw_img)

    os.system('convert full_full.bmp -resize 800x480 full.jpg')

    os.unlink('full_full.bmp')

    return 'full.jpg'

def touch(x, y, w, is_long):
    x = round(800 * x / w)
    y = round(800 * y / w)
    requests.get(f'http://localhost:8080/set_touch?x={x}&y={y}&hold={1 if is_long else 0}')

import json
import threading
import os

def get_split_imgs():
    bmp_path = backend.get_img()

    with open('crops.json') as f:
        crops = json.load(f)

    threads = []
    for crop in crops:
        threads.append(threading.Thread(target=os.system, args=(f'convert {bmp_path} -crop {crop} pieces/{crop.split("+", 1)[1].replace("+", "x")}.jpg',)))
        threads[-1].start()
    for thread in threads:
        thread.join()

    os.unlink(bmp_path)

    os.system("md5sum -c oldlist 2>/dev/null | grep FAILED > newlist")
    changed = []
    with open('newlist') as f:
        lines = f.readlines()
        for line in lines:
            changed.append(line.split(": ")[0].split('.')[0].split('/')[1])
    os.system("md5sum pieces/* > oldlist")

    return changed

def get_full_img():
    bmp_path = backend.get_img()
    
    os.system(f'convert {bmp_path} img.jpg')

    os.unlink(bmp_path)

    return 'img.jpg'

def touch(x, y, w, is_long):
    x = round(800 * x / w)
    y = round(800 * y / w)
    backend.touch(x, y, is_long)

import json
import threading
import os
import subprocess

def run(bmp_path, crop):
    subprocess.run(['convert', bmp_path, '-crop', crop, f'pieces/{crop.split("+", 1)[1].replace("+", "x")}.jpg',])

def get_split_imgs():
    bmp_path = backend.get_img()

    with open('crops.json') as f:
        crops = json.load(f)

    threads = []
    for crop in crops:
        threads.append(threading.Thread(target=run, args=([bmp_path, crop])))
        threads[-1].start()
    for thread in threads:
        thread.join()

    os.unlink(bmp_path)
    
    with open('newlist', 'w+b') as f:
        md5sum = subprocess.Popen(['md5sum', '-c', 'oldlist'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        grep = subprocess.Popen(['grep', 'FAILED'], stdin=md5sum.stdout, stdout=f)
        grep.wait()
        
    changed = []
    with open('newlist') as f:
        lines = f.readlines()
        for line in lines:
            changed.append(line.split(": ")[0].split('.')[0].split('/')[1])

    with open('oldlist', 'w+b') as f:
        subprocess.Popen(['md5sum'] + [f'pieces/{i}' for i in os.listdir('pieces')], stdout=f)

    return changed

def get_full_img():
    bmp_path = backend.get_img()
    
    subprocess.run(['convert', bmp_path, 'img.jpg',])

    os.unlink(bmp_path)

    return 'img.jpg'

def touch(x, y, w, is_long):
    x = round(800 * x / w)
    y = round(800 * y / w)
    backend.touch(x, y, is_long)

import json
import threading
import os
import subprocess

def get_img():
    bmp_path = backend.get_img()
    
    subprocess.run(['convert', bmp_path, '-define', 'webp:lossless=true', 'img.webp',])

    os.unlink(bmp_path)

    return 'img.webp'

def touch(x, y, w, is_long):
    x = round(800 * x / w)
    y = round(800 * y / w)
    backend.touch(x, y, is_long)

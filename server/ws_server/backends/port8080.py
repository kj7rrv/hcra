import requests


def get_img():
    raw_img = requests.get('http://localhost:8080/get_capture.bmp').content

    with open('img.bmp', 'wb+') as f:
        f.write(raw_img)

    return 'img.bmp'


def touch(x, y, is_long):
    requests.get(f'http://localhost:8080/set_touch?x={x}&y={y}&hold={1 if is_long else 0}')


def connect():
    pass


def disconnect():
    pass

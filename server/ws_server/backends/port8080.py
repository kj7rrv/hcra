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

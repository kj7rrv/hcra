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

import shlex


class ConfigSyntaxError(BaseException):
    pass


def loadl(lines):
    output = {}

    for line in [ i.strip() for i in lines ]:
        words = shlex.split(line, comments=True)

        if len(words) == 0:
            pass
        elif len(words) == 2:
            if words[0] in output:
                raise ConfigSyntaxError('keys cannot be redefined')
            output[words[0]] = words[1]
        else:
            raise ConfigSyntaxError('lines must consist of exactly two tokens')

    return output


def loads(string):
    return loadl(string.split('\n'))


def load(f):
    return loadl(f.readlines())

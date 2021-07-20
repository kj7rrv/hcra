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

import os

def ignore_pylab():
    return 'Darwin' == os.uname()[0]

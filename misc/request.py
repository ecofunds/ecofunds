#!/usr/bin/env python
# coding: utf-8

'''$ python request.py url
'''
import httplib
import time
import urlparse

servers = {
    "localhost": "localhost:8000"
}

def main(args):
    for env, address in servers.items():
        print("\nTesting %s...\n" % (address))
        for i in range(2):
            connection = httplib.HTTPConnection(address)
            url = urlparse.urlparse(args[1]).path
            start = time.time()
            connection.request('GET', url)
            response = connection.getresponse()
            end = time.time()
            print("Response %s" % str(end-start))

if __name__ == "__main__":
    import sys
    main(sys.argv)

import functools
import os
import sys
import redis
from configparser import ConfigParser
from select import poll
from select import POLLERR
from select import POLLHUP
from flask import Flask
from flask import render_template

redis_connection = functools.partial(
    redis.StrictRedis,
    host='broker.ocf.berkeley.edu',
    port=6378,
    ssl=True,
    db=0,
    password=None
)

def subscribe(host, password, *channels):
    rc = redis_connection(host=host, password=password)
    sub = rc.pubsub(ignore_subscribe_messages=True)
    sub.subscribe(channels)
    return sub

def main():
    # set up stdout monitoring
    p = poll()
    p.register(sys.stdout.fileno(), POLLERR | POLLHUP)

    s = subscribe('job.user')
    while True:
        message = s.get_message()
        if message and 'data' in message:
            status_message = message['data'].decode(encoding='UTF-8').replace('\n', ' ')
            test_file = open('testfile.txt', 'w')
            print(status_message, file = test_file, flush=True)
            test_file.close()
        if p.poll(0.1):
            break

if __name__ == "__main__":
    main()
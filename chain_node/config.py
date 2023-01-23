from os import environ
import random
import socket

class Config():
    PORT = environ['PORT']
    BIND_HOST = environ.get("BIND_HOST", "localhost")
    HOST = socket.gethostbyname(socket.gethostname())
    TYPE = environ['TYPE']
    NAME = environ['NAME'] + str(random.randint(1, 1000000))
    FLASK_ENV = 'development'
    DEBUG = True
    DIR_NODE_URL = 'http://directory_node:5000'

from operations import *
import socket

class Function(object):
    def __init__(self, args, body, env):
        self.args = args
        self.body = body
        self.env = env

    def __str__(self):
        return "('primitive', <function_%s>)" % id(self)

class Data(object):
    def __init__(self, *data):
        self.data = data
    def __call__(self):
        return self.data
    def __repr__(self):
        return "(" + " ".join(str(ele) for ele in self.data) + ")"
    def __getitem__(self, key):
        return self.data[key]

class Dict(object):
    def __call__(self, args):
        print args
        return dict(args)

class Machine(object):
    def __init__(self, loc, port, name="NONAME"):
        self.location = loc
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = name

    def __str__(self):
        return "('primitive', <machine_%s:%d>)" % (self.location, self.port)

class NoIdentifierFound(Exception):
    pass

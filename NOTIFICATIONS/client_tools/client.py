from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from helpers.config_parser import config_params


class Client(object):
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        PeriodicCallback(self.keep_alive, 20000, io_loop=self.ioloop).start()
        self.ioloop.start()

    @gen.coroutine
    def connect(self):
        print 'trying to connect'
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception:
            print 'connection error'
        else:
            print 'connected'
            self.run()

    @gen.coroutine
    def run(self):
        while True:
            msg = yield self.ws.read_message()
            if msg is None:
                print 'connection closed'
                self.ws = None
                break

    def keep_alive(self):
        if self.ws is None:
            self.connect()
        else:
            self.ws.write_message('keep alive')


if __name__ == '__main__':
    app_port = config_params('portserver')['port']
    host = config_params('portserver')['host']
    client = Client('ws://{0}:{1}/register?userid=bordeanu'.format(host, app_port), 5)

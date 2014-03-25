import tornado.web
import sys
import os
from rereremote import control

if getattr(sys, 'frozen', False):
    # The application is frozen (e.g. cx_freeze)
    # Static files are in the directory of the executable.
    data_dir = os.path.dirname(sys.executable)
else:
    # The application is running in an standalone interpreter, search within
    # the package.
    data_dir = os.path.dirname(__file__)

static_path = os.path.join(data_dir, 'static')


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        with open(static_path + '/index.html', 'rb') as f:
            self.write(f.read())

application = tornado.web.Application([
    ('/', IndexHandler),
    ('/control', control.ControlHandler),
], static_path=static_path)

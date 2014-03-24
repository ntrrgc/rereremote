import tornado.web
import os.path
from rereremote import control

static_path = os.path.join(os.path.dirname(__file__), 'static')

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        with open(static_path + '/index.html', 'rb') as f:
            self.write(f.read())

application = tornado.web.Application([
    ('/', IndexHandler),
    ('/control', control.ControlHandler),
], static_path=static_path)

import tornado.websocket
from tornado.log import access_log, app_log
from pykeyboard import PyKeyboard

app_key = ""
k = PyKeyboard()

class ControlHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        key = self.get_query_argument('key', '')
        if key != app_key:
            access_log.warn('Access denied on %s.' % self.request.remote_ip)
            self.write_message("Access denied")
            self.close()
        else:
            self.write_message("Access granted")
            access_log.info('Access allowed on %s.' % self.request.remote_ip)

    keys = {
        'next': k.page_down_key,
        'prev': k.page_up_key,
    }
    
    def on_message(self, message):
        try:
            vk = self.keys[message]
        except KeyError:
            app_log.error('Unknown command: %s' % message)
            return

        k.tap_key(vk)

    def on_close(self):
        access_log.info('Client %s disconnected.' % self.request.remote_ip)

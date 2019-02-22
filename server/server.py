# MIT License
#
# Copyright (c) 2019 James Coxon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import socket, time, json
import tornado.gen
import tornado.ioloop
import tornado.iostream
import tornado.tcpserver
import tornado.web
import tornado.websocket
from collections import defaultdict

client_addresses = defaultdict(list)
client_accounts = defaultdict(list)

class Data_Callback(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        receive_time = time.strftime("%d/%m/%Y %H:%M:%S")
        post_data = json.loads(self.request.body.decode('utf-8'))
#        print("{}: {}".format(receive_time, post_data))
        block_data = json.loads(post_data['block'])
        if block_data['link_as_account'] in client_addresses:
            tracking_address = block_data['link_as_account']
            clients = client_addresses[tracking_address]
            for client in clients:
                print("{}: {}".format(receive_time, client, post_data))
                client.write_message(post_data)
                print("Sent data")

class WSHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket opened: {}".format(self))

    @tornado.gen.coroutine
    def on_message(self, message):
        print('Message from client {}: {}'.format(self, message))
        if message != "Connected":
            try:
                ws_data = json.loads(message)
                if 'address' not in ws_data:
                    raise Exception('Incorrect data from client: {}'.format(ws_data))
                print(ws_data['address'])
                client_addresses[ws_data['address']].append(self)
                print(client_addresses)
                client_accounts[self].append(ws_data['address'])

            except Exception as e:
                print("Error {}".format(e))

    def on_close(self):
        print('Client disconnected - {}'.format(self))
        accounts = client_accounts[self]
        for account in accounts:
            client_addresses[account].remove(self)
            if len(client_addresses[account]) == 0:
                del client_addresses[account]
        del client_accounts[self]
        print(client_addresses)
        print(client_accounts)

application = tornado.web.Application([
    (r"/callback/", Data_Callback),
    (r"/call", WSHandler),
])


def main():

    # websocket server
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** Websocket Server Started at %s***' % myIP)

    # callback server
    application.listen(7090)

    # infinite loop
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

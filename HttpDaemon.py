from socket import socket, AF_INET, SOCK_STREAM
from Log import Log
from HttpRequest import HttpRequest
from HttpRequestHandler import HttpRequestHandler

class HttpDaemon:
    """ The main controller of the server """

    def __init__(self, options, args):
        self.host = options.host
        self.port = options.port
        HttpDaemon.options = options

    def run(self):
        Log.write('Launching daemon...')

        Log.log('Loading request handlers...')

        from handlers import HANDLERS

        Log.debug('Handlers:', [str(h) for h in HANDLERS])
        for handler in HANDLERS:
            HttpRequestHandler.addHandler(handler)

        try:
            sock = socket(AF_INET, SOCK_STREAM)

            Log.log('Binding to interface...')
            sock.bind((self.host, self.port))
            sock.listen(5)

            Log.write('Ready and listening on port', self.port)
            while True:
                conn, addr = sock.accept()
                try:
                    Log.log('\n') # newline to separate requests in console
                    Log.log('Connection request received from', addr)

                    request = HttpRequest()
                    while not request.completed:
                        received = conn.recv(1024)
                        request.append(received)

                    Log.debug('Full request:\n', request)

                    Log.log('Crafting response...')
                    response = HttpRequestHandler.handle(request)
                    Log.debug('Sending response:\n', str(response))
                    conn.sendall(str(response))
                    Log.log('Response sent')
                finally:
                    Log.log('Closing connection to', addr)
                    conn.close()
        finally:
            Log.log('Closing listening socket')
            sock.close()


from Log import Log
from HttpRequestHeader import HttpRequestHeader

class HttpRequest:
    """
    Represents a HTTP request
    
    Use append() to append data to the request.
    Do not access these until 'completed' is True:
        'header' contains the HttpRequestHeader for this request
        'body' contains a string of the body of the request
        'requestString' contains the original request as it was received.
    """
    def __init__(self):
        self.completed = False
        self.requestString = ''
        self.header = None
        self.body = None

    def append(self, data):
        self.requestString += data
        if self.header is None:
            eoh = data.find('\r\n\r\n')
            if eoh >= 0:
                Log.log('Header received.')
                self.header = HttpRequestHeader()
                self.header.parse(data[:eoh])
                self.body = data[eoh+4:]

                self.completed = self.completed or \
                        self.header.parseError or \
                        len(self.body) >= int(self.header.field('Content-Length'))
        else:
            self.body += data
            self.completed = self.completed or \
                        len(self.body) >= int(self.header.field('Content-Length'))

    def __str__(self):
        return str(self.header) + '\r\n' + str(self.body)

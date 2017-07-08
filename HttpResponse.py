from Log import Log
from HttpResponseHeader import HttpResponseHeader

class HttpResponse:
    """
    Represents a HTTP response.
    
    'header' contains the header of the response.
    'body' contains the body of the response.
    """
    def __init__(self):
        self.header = HttpResponseHeader()
        self.body = ''

    def __str__(self):
        return str(self.header) + '\r\n' + self.body

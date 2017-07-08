from Log import Log
from HttpResponse import HttpResponse

class HttpRequestHandler:
    """ Handles the requests """

    # Dictionary of endpoints and their associated handlers
    handlers = {}

    @staticmethod
    def addHandler(handler):
        """ Adds a handler to the list of handlers we delegate work to. """
        for target in handler.handles:
            Log.log(handler, 'wishes to handle requests to', target['endpoint'],
                             'allowing the methods', target['methods'])
            HttpRequestHandler.handlers[target['endpoint']] = {
                'handler': handler,
                'methods': target['methods']
            }

    @staticmethod
    def handle(request):
        """ Process the request; return our response. """
        response = HttpResponse()

        # We don't support connection: keep-alive
        response.header.setField('Connection', 'close')

        # A slight vanity license plate
        response.header.setField('Server', 'SebHTTPd')

        # Treat HEAD-requests as GETs
        isHead = False
        if request.header.method == 'HEAD':
            request.header.method = 'GET'
            isHead = True

        if request.header.parseError:
            # Bad Request
            response.header.status = '400'
            Log.log('400 - error parsing the header')
        elif request.header.method == 'TRACE':
            # Trace returns the original request in the message body.
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html#sec9.8
            response.header.status = '200'
            response.header.setField('Content-Type', 'message/http')
            response.body = request.requestString
        else:
            target = request.header.uri.target
            Log.log('target =', target, '- resource =', request.header.uri.resource)
            if target in HttpRequestHandler.handlers:
                handler = HttpRequestHandler.handlers[target]
                Log.log(handler['handler'], 'handles that endpoint')
                if request.header.method in handler['methods']:
                    handler['handler'].handle(request, response)
                else:
                    # Method Not Allowed
                    Log.log('405 - method was', request.header.method, 'expected one of', handler['methods'])
                    response.header.status = '405'
            else:
                # File Not Found
                Log.log('404 - nothing handles that endpoint')
                response.header.status = '404'

        # If it is a HEAD request, strip out the body
        if isHead:
            response.body = ''

        # Finally, updat the content length appropriately.
        response.header.setField('Content-Length', str(len(response.body)))

        return response


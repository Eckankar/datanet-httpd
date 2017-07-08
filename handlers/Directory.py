from Handler import Handler
from Log import Log
from os import getcwd, chdir

class Directory(Handler):
    """
    Prints/changes current working directory of the server.
    """

    handles = [
        { 'endpoint': 'pwd',
          'methods': ['GET'] },
        { 'endpoint': 'cwd',
          'methods': ['PUT'] }
    ]

    def handle(self, request, response):
        if request.header.uri.target == 'pwd':
            response.body = getcwd()
            response.header.status = '200'
            Log.log('200 - Successful request')
        elif request.header.uri.target == 'cwd':
            if not request.header.field('Content-Type').lower() in ['text/plain']:
                response.header.status = '415' # Unsupported Media Type
                Log.log("415 - Didn't provide us with a plaintext path.")
                return
            try:
                chdir(request.body)
                response.body = getcwd()
                response.header.status = '200'
                Log.log('200 - Successful request; working directory set to ',
                        request.body)
            except OSError:
                response.header.status = '403' # Forbidden
                Log.log('403 - Unable to change directory to', request.body)


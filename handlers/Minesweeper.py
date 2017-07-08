from Handler import Handler
from Log import Log

class Minesweeper(Handler):
    """ Logs the current Minesweeper highscore """

    handles = [
        { 'endpoint': 'minesweeper',
          'methods': ['GET', 'PUT'] }
    ]

    def __init__(self):
        self.highscore = 999

    def handle(self, request, response):
        if request.header.method == 'GET':
            response.body = 'The current Minesweeper highscore is ' + \
                            str(self.highscore) + ' seconds on Expert.'
            response.header.status = '200'
            response.header.setField('Content-Type', 'text/plain')
            Log.log('200 - Successful request')
        elif request.header.method == 'PUT':
            if not request.header.field('Content-Type').lower() in ['text/plain']:
                response.header.status = '415' # Unsupported Media Type
                Log.log("415 - Didn't provide us with a plaintext highscore.")
                return

            if not request.body.isdigit():
                response.header.status = '400' # Bad Request
                Log.log('400 - Non-integral body of message not acceptable.')
                return

            score = int(request.body)
            if 0 < score and score < self.highscore:
                response.header.status = '204' # No Content
                Log.log('204 - Highscore successfully changed from',
                        self.highscore, 'to', score)
                self.highscore = score
            else:
                response.header.status = '400' # Bad Request
                Log.log('400 - Score outside of legal range.')




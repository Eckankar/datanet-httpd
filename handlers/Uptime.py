from Handler import Handler
from Log import Log

class Uptime(Handler):
    """ Displays the current system uptime. """

    handles = [
        { 'endpoint': 'uptime',
          'methods':  ['GET'] }
    ]

    def handle(self, request, response):
        # Method based off of
        # http://thesmithfam.org/blog/2005/11/19/python-uptime-script/ 

        try:
            Log.log('Fetching uptime from /proc/uptime...')
            f = open('/proc/uptime')
            seconds = int(f.read().split('.')[0])
            f.close()
        except:
            Log.log("503 - Oops, guess that didn't work; non-Linux system?")
            response.header.status = '503'
            return

        MINUTE = 60
        HOUR = 60 * MINUTE
        DAY = 24 * HOUR

        days    =  seconds // DAY
        hours   = (seconds % DAY) // HOUR
        minutes = (seconds % HOUR) // MINUTE
        seconds =  seconds % MINUTE

        # Make a list of the different parts of the uptime ready for joining later
        output = [ str(num) + ' ' + name + (num == 1 and [''] or ['s'])[0] # NB: and/or trick needs lists,
                   for (num, name) in [(days, 'day'),                      #     as '' evaluates to false.
                                       (hours, 'hour'),
                                       (minutes, 'minute'),
                                       (seconds, 'second')]
                   if num > 0]

        response.body = 'System uptime: '+', '.join(output)
        response.header.status = '200'
        response.header.setField('Content-Type', 'text/plain')
        Log.log('200 - Successful request')




from Handler import Handler
from Log import Log
from os import uname

class SysInfo(Handler):
    """ Displays which OS the system is running on. """

    handles = [
        { 'endpoint': 'sysinfo',
          'methods': ['GET'] }
    ]

    def handle(self, request, response):
        response.body = ' '.join(uname())
        response.header.status = '200'
        Log.log('200 - Successful request')

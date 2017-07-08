from Log import Log
from HttpHeader import HttpHeader
from Uri import Uri
import re

class HttpRequestHeader(HttpHeader):
    """
    Represents the header of a HTTP request.
    

    'parseError' is a bool that says whether the header processing failed or not.
    'method' contains the method used (GET/POST/HEAD/...)
    'uri' contains a Uri object representing the requested URL
    'version' contains the version number of the request.
    """

    def parse(self, requestString):
        """ Populate the header based on an input string. """
        self.parseError = False

        lines = requestString.splitlines()

        Log.log('Parsing request-line...')
        requestLine = lines[0].split(' ')
        if len(requestLine) != 3:
            Log.log('Malformed request-line.')
            self.parseError = True
            return

        self.method = requestLine[0].upper()

        # The URI can have 3 forms; absoluteURI, abs_path, authority
        # We transform absoluteURI to abs_path for convenience
        uri = requestLine[1]
        uri = re.sub(r'^http://.*?(?=/)', '', uri)
        self.uri = Uri(uri)
        self.parseError = self.parseError or self.uri.parseError

        self.version = requestLine[2].upper()

        Log.debug('(method, uri, version) =', (self.method, str(self.uri), self.version))

        for line in lines[1:]:
            field, _, value = line.partition(':')
            self.setField(field, value)

        Log.debug('Fields:', self.fields)

    def __str__(self):
        return self.method + ' ' + str(self.uri) + ' ' + self.version + '\r\n' + \
               HttpHeader.__str__(self)

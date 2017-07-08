from Log import Log

class Uri:
    """
    Represents an URI
    
    'originalUri' contains the string originally used to represent the target

    'target' contains the handler targeted
    'resource' contains the resource requested on the handler
    'query' contains the query string passed

    To visualize: /target/resource?query
    Would have:
    target = target
    resource = resource
    query = query
    """
    def __init__(self, uri):
        self.parseError = False
        self.originalUri = uri

        # ? is reserved and should only exist at most once in an URI
        path, _, query = uri.partition('?')

        try:
            path = Uri.uriDecode(path).lower().split('/', 2)

            self.target = path[1]
            if len(path) > 2:
                self.resource = path[2]
            else:
                self.resource = None

            self.query = Uri.uriDecode(query)

        except:
            self.parseError = True


    @staticmethod
    def uriDecode(text):
        """ Decodes a string from percent encoding. (RFC2396) """
        i = 0
        output = ''
        while i < len(text) - 2:
            if text[i] != '%':
                output += text[i]
                i += 1
                continue

            # Each character is represented by a 2-digit hex-value
            sixteens = '0123456789ABCDEF'.find(text[i+1].upper())
            ones     = '0123456789ABCDEF'.find(text[i+2].upper())
            if sixteens == -1 or ones == -1: # Not a valid hex-value
                raise SyntaxError()

            value = 16 * sixteens + ones
            output += chr(value)
            i += 3
        output += text[-2:]
        return output

    def __str__(self):
        return self.originalUri


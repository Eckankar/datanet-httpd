class HttpHeader:
    """ Represents a HTTP header. """

    def __init__(self):
        self.fields = {}
        # unless otherwise specified; Content-Length = 0
        self.fields['Content-Length'] = '0'


    def field(self, name):
        """ Accessor to fields in the header """
        try:
            return self.fields[name.title()]
        except KeyError:
            return ''

    def setField(self, name, value):
        """ Add/replace a field in the header """
        self.fields[name.title()] = str(value).strip()

    def __str__(self):
        output = ''
        for field, value in self.fields.iteritems():
            output += field + ': ' + value + '\r\n'
        return output


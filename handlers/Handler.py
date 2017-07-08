from Log import Log

class Handler:
    """ Abstract class that defines what a request handler must do. """

    """
    The handled endpoints
    
    Should be a list of dictionaries, where each dictionary has the following entries:
        'endpoint' => An absolute path (string) to a resource this handler is willing to handle.
        'methods'  => A list of methods (string) this handler is willing to accept for the given endpoint.

    Example:
    handles = [
        { 'endpoint': 'test',
          'method'  : ['GET', 'POST'] }
    ]
    """
    handles = []

    def handle(self, request, response):
        """
        Handles the given HttpRequest.

        The given HttpResponse in the one that will be returned to the client.

        Will only be called if the client visits an endpoint listed in 'handles'.
        """
        pass

    ## For pretty printing in debug-mode: 
    def __str__(self):
        return self.__class__.__name__

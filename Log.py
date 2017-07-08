class Log:
    """
    Logs to screen

    write always logs
    log logs if verbose
    debug logs if very verbose
    """

    verbose = True
    veryVerbose = False

    @staticmethod
    def write(*message):
        for part in message:
            print str(part),
        print ''

    @staticmethod
    def log(*message):
        if Log.verbose: Log.write(*message)

    @staticmethod
    def debug(*message):
        if Log.veryVerbose: Log.write(*message)

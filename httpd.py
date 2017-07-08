#!/usr/bin/env python
from HttpDaemon import HttpDaemon
from Log import Log
from optparse import OptionParser

def main():
    # Parse commandline parameters
    parser = OptionParser()
    parser.add_option('-p', '--port', type='int',
                      default=8080, dest='port',
                      help='port the httpd should listen on')
    parser.add_option('-i', '--host', type='string',
                      default='', dest='host',
                      help='host interface to listen on')
    parser.add_option('-v', action='store_const',
                      const='verbose',
                      default='verbose', dest='verbose',
                      help='verbose output')
    parser.add_option('-V', action='store_const',
                      const='veryverbose',
                      dest='verbose', help='very verbose output')
    parser.add_option('-q', action='store_const',
                      const='quiet', dest='verbose',
                      help='non-verbose output')
    parser.add_option('--join-dht', type='string',
                      default=None, dest='initialPeer',
                      help='address of initial peer for the DHT')
    (options, args) = parser.parse_args()

    Log.verbose = options.verbose.find('verbose') > -1
    Log.veryVerbose = options.verbose == 'veryverbose'

    daemon = HttpDaemon(options, args)
    try:
        daemon.run()
    except KeyboardInterrupt:
        Log.write('Received ^C; terminating...')
        pass

if __name__ == '__main__':
    main()

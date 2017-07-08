from Handler import Handler
from Log import Log
from random import randint
from HttpDaemon import HttpDaemon
import httplib
import json

# Location of this server
SERVER_LOCATION = '127.0.0.1:' + str(HttpDaemon.options.port)

M = 2147483647

class DHT(Handler):
    """ Acts as a distributed hash table. """

    handles = [
        { 'endpoint': 'dht',
          'methods': ['GET', 'PUT'] },
        { 'endpoint': 'dht-meta',
          'methods': ['GET', 'POST'] }
    ]

    def __init__(self):
        self.cache = {}
        self.table = {}

        if HttpDaemon.options.initialPeer == None:
            Log.log('DHT with no other peers.')
            self.id = randint(0, M)
            self.minHash = 0
            self.maxHash = M
            self.hashRangeWraps = False
            self.leftNeighbor = SERVER_LOCATION
            self.rightNeighbor = SERVER_LOCATION

            self.table = {
                'johnny': 'Johnny Data',
                'simon': 'Simon Data',
                'tobias': 'Tobias Data',
                'suzy': 'Suzy Data',
                'johannes': 'Johannes Data',
                'david': 'David Data'
            }
        else:
            Log.log('Attempting to join DHT at', HttpDaemon.options.initialPeer)
            gotId = False
            while not gotId:
                self.id = randint(0, M)
                Log.log('Trying id =', self.id)
                foundRange = False
                target = HttpDaemon.options.initialPeer
                while not foundRange:
                    conn = httplib.HTTPConnection(target)
                    conn.request('GET', '/dht-meta/info')
                    response = conn.getresponse().read()
                    conn.close()
                    minHash, maxHash, id = response.split('\n')
                    minHash = int(minHash)
                    maxHash = int(maxHash)
                    id = int(id)

                    conn = httplib.HTTPConnection(target)
                    conn.request('GET', '/dht-meta/neighbors')
                    response = conn.getresponse().read()
                    conn.close()
                    leftNeighbor, rightNeighbor = response.split('\n')

                    if self.hashInRange(self.id, minHash, maxHash):
                        foundRange = True
                    else:
                        oldTarget = target
                        target = self.hashDist(minHash, self.id) < self.hashDist(maxHash, self.id) \
                                 and leftNeighbor or rightNeighbor
                        Log.debug('Not in range at', oldTarget, 'asking', target, 'instead')

                gotId = self.id != id

            if self.hashInRange(self.id, minHash, id):
                self.leftNeighbor = leftNeighbor
                self.rightNeighbor = target
            else:
                self.leftNeighbor = target
                self.rightNeighbor = rightNeighbor

            Log.debug('Squeezing myself in between', self.leftNeighbor, 'and', self.rightNeighbor)

            conn = httplib.HTTPConnection(self.leftNeighbor)
            conn.request('POST', '/dht-meta/join', 'right\n' + str(self.id) + '\n' + SERVER_LOCATION)
            response = conn.getresponse().read()
            conn.close()
            minHash, data = response.split('\n', 1)
            self.minHash = int(minHash)
            data = json.loads(data)
            self.table.update(data)
            Log.log('Joined to left neighbor; received', len(data), 'elements')

            conn = httplib.HTTPConnection(self.rightNeighbor)
            conn.request('POST', '/dht-meta/join', 'left\n' + str(self.id) + '\n' + SERVER_LOCATION)
            response = conn.getresponse().read()
            conn.close()
            maxHash, data = response.split('\n', 1)
            self.maxHash = int(maxHash)
            data = json.loads(data)
            self.table.update(data)
            Log.log('Joined to right neighbor; received', len(data), 'elements')

            # We might've gotten too much data sent to us if there's only one server
            # a----b-----c----d
            # Server 1 owns a-d, we want b-c
            # Server 1 updates to c-d, sends us a-c
            # Server 1 updates to c-b
            # We now must send server 1 a-b
            data = {}
            keysToDelete = []
            for key in self.table:
                if not self.hashInRange(self.hash(key)):
                    Log.debug("Shouldn't have gotten", key, '(hash:', self.hash(key), ')')
                    data[key] = self.table[key]
                    keysToDelete.append(key)
            if len(data) > 0:
                Log.log("I got too much data; must only be one server in network")
                Log.log("Returning extra data to neighbor")
                conn = httplib.HTTPConnection(self.rightNeighbor)
                conn.request('POST', '/dht-meta/transfer', json.dumps(data))
                response = conn.getresponse().read()
                conn.close()

                for key in keysToDelete:
                    del self.table[key]

        Log.log('DHT id is', self.id, 'which makes me handle requests from', self.minHash, 'to', self.maxHash)
        Log.log('I contain', len(self.table), 'elements')


    def handle(self, request, response):
        resource = request.header.uri.resource
        if request.header.uri.target == 'dht':
            hash = self.hash(resource)
            Log.log('Requested resource', resource, 'has hash', hash)

            if request.header.method == 'GET':
                Log.log(self.minHash, hash, self.maxHash)
                if self.hashInRange(hash):
                    Log.log('I handle that hash')
                    if resource not in self.table:
                        response.header.status = '404' # File Not Found
                        Log.log("404 - Element doesn't exist in table.")
                        return
                    else:
                        response.header.status = '200' # OK
                        response.body = self.table[resource]
                        return
                elif resource in self.cache:
                    Log.log('I have that one cached')
                    response.header.status = '200' # OK
                    response.body = self.cache[resource]
                    return
                else:
                    target = self.hashDist(self.minHash, hash) < self.hashDist(self.maxHash, hash)\
                                and self.leftNeighbor or self.rightNeighbor
                    Log.log("That's out of my range; I'll ask", target, 'for it')
                    conn = httplib.HTTPConnection(target)
                    conn.request('GET', '/dht/' + resource)
                    resp = conn.getresponse()
                    conn.close()
                    response.header.status = str(resp.status)
                    response.body = resp.read()
                    Log.log("Storing data for", resource, "in cache")
                    self.cache[resource] = response.body
                    Log.log('Cache now contains', len(self.cache), 'elements')
                    return

            if request.header.method == 'PUT':
                if self.hashInRange(hash):
                    Log.log('I handle that hash')
                    Log.log('Invalidating cache entries on network')
                    direction = request.header.field('X-Last-Node') == self.rightNeighbor\
                                and 'left' or 'right'
                    target = direction == 'left' and self.leftNeighbor or self.rightNeighbor
                    entry = request.header.field('X-Initial-Entry') or SERVER_LOCATION
                    while target != entry:
                        conn = httplib.HTTPConnection(target)
                        conn.request('POST', '/dht-meta/invalidate', resource + '\n' + direction)
                        resp = conn.getresponse()
                        conn.close()
                        target = resp.read()

                    Log.log('Updating value for', resource)
                    response.header.status = '204' # No Content
                    self.table[resource] = request.body
                    return
                else:
                    target = self.hashDist(self.minHash, hash) < self.hashDist(self.maxHash, hash)\
                                and self.leftNeighbor or self.rightNeighbor
                    Log.log('Clearing',resource, 'from cache')
                    if resource in self.cache:
                        del self.cache[resource]
                    Log.log('Cache now contains', len(self.cache), 'elements')
                    Log.log("That's out of my range; I'll give it to", target)
                    conn = httplib.HTTPConnection(target)
                    conn.request('PUT', '/dht/' + resource, request.body, {
                        'X-Initial-Entry': request.header.field('X-Initial-Entry')\
                                           or SERVER_LOCATION,
                        'X-Last-Node': SERVER_LOCATION
                    })
                    resp = conn.getresponse()
                    conn.close()
                    response.header.status = str(resp.status)
                    response.body = resp.read()
                    return

        elif request.header.uri.target == 'dht-meta':
            if request.header.method == 'GET':
                if resource == 'info':
                    response.header.status = '200' # OK
                    response.body = str(self.minHash) + '\n' + str(self.maxHash) + '\n' + str(self.id)
                    return
                if resource == 'neighbors':
                    response.header.status = '200' # OK
                    response.body = self.leftNeighbor + '\n' + self.rightNeighbor
                    return
                if resource == 'data':
                    response.header.status = '200' # OK
                    response.body = 'My data:\n\n'
                    for d in self.table:
                        response.body += str(self.hash(self.table[d])) + ' - ' + d + \
                                         ' - ' + self.table[d] + '\n'
                    response.body += '\nMy cached data:\n\n'
                    for d in self.cache:
                        response.body += str(self.hash(self.cache[d])) + ' - ' + d + \
                                         ' - ' + self.cache[d] + '\n'
                    return
            elif request.header.method == 'POST':
                if resource == 'join':
                    side, id, location = request.body.split('\n')

                    id = int(id)
                    dId = self.hashDist(id, self.id)
                    if side == 'left':
                        self.leftNeighbor = location
                        self.minHash = (self.id - (dId+1)//2) % (M+1)
                        Log.log('Left neighbor adjusted to', self.leftNeighbor)
                        Log.log('Minimum has adjusted to', self.minHash)
                        response.body = str((self.minHash-1)%(M+1)) + '\n'
                    elif side == 'right':
                        self.rightNeighbor = location
                        self.maxHash = (self.id + dId//2) % (M+1)
                        Log.log('Right neighbor adjusted to', self.rightNeighbor)
                        Log.log('Maximum hash adjusted to', self.maxHash)
                        response.body = str((self.maxHash+1)%(M+1)) + '\n'

                    data = {}
                    keysToDelete = []
                    for key in self.table:
                        if not self.hashInRange(self.hash(key)):
                            Log.debug('I no longer own', key, '(hash:', self.hash(key), ')')
                            data[key] = self.table[key]
                            keysToDelete.append(key)

                    response.body += json.dumps(data)
                    response.header.status = '200' # OK
                    Log.log('Transfered', len(data), 'elements to new server.')

                    for key in keysToDelete:
                        del self.table[key]
                    Log.log('I now contain', len(self.table), 'elements')
                    return
                elif resource == 'transfer':
                    Log.log('Inserting data into table')
                    data = json.loads(request.body)
                    for key in data:
                        self.table[key] = data[key]
                    Log.log('I now contain', len(self.table), 'elements')
                    response.status = '204' # No Content
                    return
                elif resource == 'invalidate':
                    key, direction = request.body.split('\n')
                    if key in self.cache:
                        Log.log('Clearing', key, 'from cache')
                        del self.cache[key]
                        Log.log('Cache now contains', len(self.cache), 'elements')
                    response.body = direction == 'right' and self.rightNeighbor\
                                                          or self.leftNeighbor
                    response.status = '200' # OK

    def hashDist(self, h1, h2):
        """ Returns the minimum distance from one hash to another. """
        MM = M+1
        return min((h1 + MM - h2) % MM, (h2 + MM - h1) % MM)


    def hashInRange(self, hash, minHash=None, maxHash=None):
        """ Is the hash covered by the range? """
        if minHash == None:
            minHash = self.minHash

        if maxHash == None:
            maxHash = self.maxHash

        if hash == minHash or hash == maxHash:
            return True

        if minHash > maxHash:
            return not self.hashInRange(hash, maxHash, minHash)

        return minHash < hash and hash < maxHash


    def hash(self, string):
        """
        Hashes a string

        Returns the SDBM-hash of a string.
        0 <= hash <= M
        """
        hash = 0
        for ch in string:
            hash = ord(ch) + (hash << 6) + (hash << 16) - hash
        return hash & M

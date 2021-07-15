# This code is from Brian Muller's Kademlia project. This server acts as 
# a bootstrap server when an existing kademlia network is not available.

# Copyright (c) 2014 Brian Muller

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#from twisted.application import service, internet
#from twisted.python.log import ILogObserver
#from twisted.internet import reactor, task
import asyncio

import sys, os
sys.path.append(os.path.dirname(__file__))
from kademlia.network import Server

logfile = open("logs/twistd-logging.log", "a")

def log(eventDict):
    # untilConcludes is necessary to retry the operation when the system call
    #     # has been interrupted.
    untillConcludes(logfile.write, "Got a log! {}\n".format(eventDict))
    untilConcludes(logfile.flush)
    #

#application = service.Application("kademlia") #Replace with asyncio
#application.setComponent(ILogObserver, log) #Replace with logging
loop = asyncio.get_event_loop()
if os.path.isfile('cache.pickle'):
    kserver = Server.load_state('cache.pickle')
else:
    kserver = Server()
    kserver.listen(8468)
    default=("127.0.0.1", 8468)
    kserver.bootstrap([("127.0.0.1", 8468)])
    #loop.run_until_complete(kserver.bootstrap([default])
kserver.save_state_regularly('cache.pickle', 10)

#server = internet.UDPServer(8468, kserver.protocol) #Replace with asyncio
server.setServiceParent(application)
reactor.run() #Replace with asyncio

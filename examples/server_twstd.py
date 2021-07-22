from twisted.application import service, internet
from twisted.python.log import ILogObserver
from twisted.internet import asyncioreactor, task
import sys, os, logging, asyncio
from asyncio import ensure_future

sys.path.append(os.path.dirname(__file__))
from kademlia.network import Server

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)
loop=asyncio.get_event_loop()
loop.set_debug(True)

asyncioreactor.install(evetloop=loop)



if os.path.isfile('cache.pickle2'):
    kserver = Server.loadState('cache.pickle2')
else:
    kserver = Server()
    kserver.listen(8468)
    ensure_future(kserver.bootstrap([("192.168.56.101", 8468)]))
kserver.saveStateRegularly('cache.pickle2', 10)


server = internet.UDPServer(8468, kserver.protocol)
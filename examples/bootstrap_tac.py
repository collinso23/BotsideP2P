import logging, os, sys
import asyncio
sys.path.append(os.path.dirname(__file__))

from kademlia.network import Server

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)


loop = asyncio.get_event_loop()
loop.set_debug(True)


if os.path.isfile('cache.pickle'):
    kserver = Server.loadState('cache.pickle')
else:
    kserver = Server()
    loop.run_until_complete(kserver.bootstrap([("127.0.0.1", 8468)]))

kserver.saveStateRegularly('cache.pickle', 10)

loop.run_until_complete(kserver.listen(8468))

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    kserver.stop()
    loop.close()
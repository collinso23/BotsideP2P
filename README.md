# P2P Botnet.
This is just a proof of concept, used for educational purposes, and should not in any way be used maliciously. 

##Dependencies

This P2P botnet requires Python 3.5+ and the following Python libraries:
* [Kademlia] - a Python implementation of the [Kademlia distributed hash table]

On an Ubuntu machine all of the requirements can be installed by running the following commands:
```
./install.sh
```
Windows and MacOS have not been tested.

In addition to the requirements to run the project, the botnet also needs three different machines that can communicate over a network. This can be done in virtual machines or physical machines, but each machine must be able to communicate with the other machines and must have the above dependencies installed.

##Usage

The botnet consists of three primary components:
* botnet.py - client node that communicates with other nodes and waits for commands from a commander
* commander.py - command module to send commands to enslaved nodes in the botnet
* bootstrapServer.py - a kademlia server for clients to bootstrap into the network

To use the botnet, perform the following commands on 3 separate machines.
* Step 1: Start Bootstrap Server
```
python bootstrap_tac.py
```
* Step 2: Start Command Module
```
python commander.py [bootstrap ip][bootstrap port][commander port]
```
*Note: default bootstrap port is 8468, this can be changed in server.tac*

* Step 3: Start Botnet Client
```
python botnet.py [bootstrap ip][bootstrap port][botnet port]
```
At this point you should have 3 different windows open. From the commander window, you have the option to type in commands for the various modules that are included.


*Server Window:*

![TODO: Add image](Screenshots/)

*Command Window:*

![TODO: Add image](Screenshots/)

*Botnet Window:*

![TODO: Add image](Screenshots/)


##Possible Improvements

In addition I would add more security features including digitally signed commands, and more unpredictable check in hash locations. The botnet is sending cleartext commands in the DHT which should be encrypted. 

##Authors
* [Orion Collins](https://github.com/jhoward321) - *Botnet implementation* 
* [Adam Bueachaine](https://github.com/dionesh) - *Botnet implementation*

##License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

[Kademlia]:https://github.com/bmuller/kademlia
[Kademlia distributed hash table]:https://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf

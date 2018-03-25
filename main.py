import json
import urllib2
import datetime
from datetime import datetime, date, timedelta
import os, time, httplib
from termcolor import colored
import time




url = [
    "35.184.206.51:46657",
    "35.224.148.135:46657"
]


# Monitor that site is up and running
def site_running(i):
    conn = httplib.HTTPConnection(i, timeout=10)
    try:
        conn.request("HEAD", "/")
        response = conn.getresponse()
        if response.status == 200:
            print colored(i + ' - ' + response.reason, 'green')
    except:
        print colored("Cannot reach " + i, 'red')
        pass
    conn.close()



# Check if block time is under 2min
def status(i):
    global block_height 
    # create class
    class Status():
        def __init__(self, json):
            self.status=json["result"]

    url_data = json.load(urllib2.urlopen("http://"+ i + "/status"))
    foo = Status (url_data)
    block_height =  foo.status['latest_block_height']
    latest_block_time = foo.status['latest_block_time']
    block_time =  datetime.strptime(latest_block_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    delta = datetime.utcnow() - block_time
    if block_time < datetime.utcnow() -timedelta(seconds=120):
        print colored("Late block - public consensus error! Delay " + str(delta), 'red')
        # print colored("Late block - public consensus error!",'red')
        print colored("Latest block time (utc) - " + str(block_time), 'green')
        print colored("Latest block height - " + str(block_height), 'green')
    else:
        print colored("Consensus - OK", 'green')
        print colored("Lastest block time (utc) - " + str(block_time), 'green')
        print colored("Latest block height - " + str(block_height), 'green')
     


# Check if sufficient # of nodes are available
def net_info(i):
    global node_ip
    # create class
    class Info():
        def __init__(self, json):
            self.info=json["result"]["peers"]

    url_data = json.load(urllib2.urlopen("http://"+ i + "/net_info"))
    foo = Info (url_data)
    if len(foo.info) == 1:
        print colored("Insufficient nodes - under 5 nodes available!  Current count " + str(len(foo.info)) + " node", 'red')
    if 1 < len(foo.info) < 5:
        print colored("Insufficient nodes - under 5 nodes available!  Current count " + str(len(foo.info)) + " nodes", 'red')
    else:
        print colored("Current number of nodes - " + str(len(foo.info)), 'green')

    # get list of node IP addresses 
    node_ip = []
    for k in foo.info:
      node_ip.append(k['node_info']['listen_addr'])



# Check if all block heights are in sync
def dump_consensus(i):
    #create class
    class Dump():
        def __init__(self, json):
            self.dump=json["result"]["peer_round_states"]

    url_data = json.load(urllib2.urlopen("http://"+ i + "/dump_consensus_state"))

    #get peer round states to check what validators think the block heigh should be
    state = Dump (url_data)
    for k in node_ip:
        try:
            # compare peer round states to actual block height for consensus
            if state.dump[k]['Height'] != block_height+1:
                print colored("Block height different - " + k + ' ' + "(height " + str(state.dump[k]['Height'])+ ")", 'red')
            else:
                pass
        except:
            pass
        try:
            if state.dump["891023d33e161bafff356b74ea44730d295342b9"]['Height'] != block_height+1:
                print colored("Block height different - " + ' ' + "(height " + str(state.dump["891023d33e161bafff356b74ea44730d295342b9"]['Height'])+ ")", 'red')
            else:
                pass
        except:
            pass



# saved in db
last_run = 16908


# Scan all blocks
def scan(i):
    #create classes
    class Block():
        def __init__(self, json):
            self.block=json["result"]["block"]["last_commit"]["precommits"]

    class BlockHeight():
        def __init__(self, json):
            self.blockheight=json["result"]["block"]["header"]


    class ValidatorsHeight():
        def __init__(self, json):
            self.validatorsheight=json["result"]


    def get_height_urls():
        global url_block, url_validators 

        if last_run <= block_height:
            start = last_run 
        else:
            start = block_height
        end = block_height + 1
        url_block = []
        url_validators = []
        

        for number in range (start, end):
            block = ("http://"+ i + "/block?height=" + str(number))
            validators_height = ("http://"+ i + "/validators?height=" + str(number))
            url_block.append(block)
            url_validators.append(validators_height)
 
    get_height_urls()

    
    # count block validators
    print colored ("Scanning all blocks...", 'green')
    total_blocks = len(url_block)
    blockcount = dict()
    block_validators_list = dict()
    for i in url_block:
        url_data = json.load(urllib2.urlopen(i))
        foo = Block (url_data) 
        header = BlockHeight (url_data)
        block_height_at = header.blockheight['height']
        block_validators = []
        # print("Got " + i)
        for k in foo.block:
                try:
                    if k['validator_address']:
                        block_validators.append(k['validator_address'])
                        if k['validator_address'] not in blockcount:
                            blockcount[k['validator_address']] = 1
                        else:
                            blockcount[k['validator_address']] += 1
                except:
                    pass

        block_validators_list[block_height_at] = block_validators

        
    # get % of blocks validator participated in out of all blocks committed
    for key, value in blockcount.items():
        participation = (value * 100) / total_blocks
        print(key +" "+ str(participation) + '%')

    # count validator validators 
    print colored ("Calculating uptime...", 'green')
    validatorscount = dict()
    validator_validators_list = dict()
    for i in url_validators:
        url_data = json.load(urllib2.urlopen(i))
        foo = ValidatorsHeight (url_data)
        validators_block_height_at = foo.validatorsheight['block_height']
        validator_validators = [] 
        # print("Got " + i)
        for k in foo.validatorsheight['validators']:
            try:
                if k['address']:
                    validator_validators.append(k['address'])
                    if k['address'] not in validatorscount:
                        validatorscount[k['address']] = 1
                    else:
                        validatorscount[k['address']] += 1  
            except:
                pass

        validator_validators_list[validators_block_height_at] = validator_validators


    # calculate uptime for each validator 
    for key in blockcount:
        expected = validatorscount[key]
        actual = blockcount[key]
        uptime = (actual * 100) / expected
        print(key +" "+ str(uptime) + '%')

    
    # get difference btw expected validators and actual block validators 
    delta = {}
    for key in block_validators_list:
        delta[key] = list(set(validator_validators_list[key]) - set(block_validators_list.get(key, [])))


    # alert if block not signed by all validators
    for key, value in delta.items():
        if value != []:
            print colored(str(value) + " did not sign block " + str(key), 'red')
        else:
            pass


    # alert if three consecutive blocks not signed by validator
    for n in validator_validators:
        if any (n in val for val in delta.values()):
            # get the keys with missing values
            keys = [key for key, value in delta.items() if n not in value]
            # check if 3 entries are consecutive
            subs = [keys[i:i+3] for i in range(len(keys)) if len(keys[i:i+3]) == 3]
            if len(subs) > 2:
                print colored(n + " has missed three consecutive blocks ", 'red')
                print subs[0]
                print "Total blocks missed " + str(keys)


# Global loop for list of urls
for i in url:
    site_running(i)
    status(i)
    net_info(i)
    dump_consensus(i)
    scan(i)
    print '\n'


# Run scan function in regular intervals
while(True):
    for i in url: 
            scan(i)
            print '\n'
    time.sleep(120)




    

        



  
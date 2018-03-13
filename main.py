import json
import urllib2
import datetime
from datetime import datetime, date, timedelta
import os, time, httplib
from termcolor import colored


url = [
    "35.204.86.158:46657",
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
        print colored("Lastest block time (utc) - " + str(block_time), 'green')
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
    if len(foo.info) < 5:
        print colored("Insufficient nodes - under 5 nodes available!  Current count " + str(len(foo.info)) + " nodes", 'red')
    else:
        print colored("Current number of nodes - " + str(len(foo.info)), 'green')

    # get list of node IP addresses 
    node_ip = []
    for k in foo.info:
      node_ip.append(k['node_info']['listen_addr'])



# Check if all block heighs are in sync
def dump_consensus(i):
    #create class
    class Dump():
        def __init__(self, json):
            self.dump=json["result"]["peer_round_states"]

    url_data = json.load(urllib2.urlopen("http://"+ i + "/dump_consensus_state"))
    state = Dump (url_data)
    for k in node_ip:
        # print state.dump[k]['Height']
        if state.dump[k]['Height'] != block_height+1:
            print colored("Block height different - " + k + ' ' + "(height " + str(state.dump[k]['Height'])+ ")", 'red')
        else:
            pass

# Scan all blocks
def scan(i):
    #create classes
    class Block():
        def __init__(self, json):
            self.block=json["result"]["block"]["last_commit"]["precommits"]

    class ValidatorsHeight():
        def __init__(self, json):
            self.validatorsheigh=json["result"]["validators"]

    start = block_height - 5
    end = block_height + 1
    url_block = []
    url_validators = []

    for number in range (start, end):
        block = ("http://"+ i + "/block?height=" + str(number))
        validators_height = ("http://"+ i + "/validators?height=" + str(number))
        url_block.append(block)
        url_validators.append(validators_height)

    # count block validators
    total_blocks = len(url_block)
    blockcount = dict()
    print colored ("Scanning all blocks...", 'green')
    for i in url_block:
        url_data = json.load(urllib2.urlopen(i))
        foo = Block (url_data)
        # print("Got " + i)
        for k in foo.block:
                try:
                    if k['validator_address']:
                        if k['validator_address'] not in blockcount:
                            blockcount[k['validator_address']] = 1
                        else:
                            blockcount[k['validator_address']] += 1
                except:
                    pass

    for key, value in blockcount.items():
        participation = (value * 100) / total_blocks
        print(key +" "+ str(participation) + '%')


    # count validators at block height 
    print colored ("Calculating uptime...", 'green')
    validatorscount = dict()
    for i in url_validators:
        url_data = json.load(urllib2.urlopen(i))
        foo = ValidatorsHeight (url_data)
        # print("Got " + i)
        for k in foo.validatorsheigh:
            try:
                if k['address']:
                    if k['address'] not in validatorscount:
                        validatorscount[k['address']] = 1
                    else:
                        validatorscount[k['address']] += 1  
            except:
                pass

    # calculate uptime
    for key in blockcount:
        expected = validatorscount[key]
        actual = blockcount[key]
        uptime = (actual * 100) / expected
        print(key +" "+ str(uptime) + '%')

    

# Global loop for url list
for i in url:
    try:
        site_running(i)
        status(i)
        net_info(i)
        dump_consensus(i)
        scan(i)
        print '\n'
    except:
        pass


        



  
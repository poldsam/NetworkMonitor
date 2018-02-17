import json
import urllib2
from datetime import datetime, date, timedelta
import os, time, httplib
from termcolor import colored


url = [
    "35.204.86.158:46657",
]


# Monitor that site is up and running
def site_running():
# while (True):
    for i in url:
        conn = httplib.HTTPConnection(i, timeout=10)
        try:
            conn.request("HEAD", "/")
            response = conn.getresponse()
            if response.status == 200:
            	print colored(i + ' ' + response.reason , 'green')
    	except:
    		print colored("Cannot reach " + i, 'red')
    		pass
        conn.close()
    # time.sleep(1000)
site_running()



# create global classes
class Status():
    def __init__(self, json):
    	self.status=json["result"]

class Info():
    def __init__(self, json):
    	self.info=json["result"]["peers"]

class Dump():
    def __init__(self, json):
    	self.dump=json["result"]["peer_round_states"]


# Check block status and % of blocks committed by each validator
def status():
  	# get subdomain urls      
    url_status = []
    for i in url:
    	url_status.append("http://"+ i + "/status")

    url_net_info = []
    for i in url:
    	url_net_info.append("http://"+ i + "/net_info")

    url_dump = []
    for i in url:
    	url_dump.append("http://"+ i + "/dump_consensus_state")


	# check if block time is under 2min
    for i in url_status:
        url_data = json.load(urllib2.urlopen(i))
        foo = Status (url_data)
        block_height =  foo.status['latest_block_height']
        block_time =  datetime.strptime(foo.status['latest_block_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        delta = (datetime.utcnow() - block_time).days * 24 * 60
        if block_time < datetime.utcnow()-timedelta(seconds=120):
            print colored("Late block - public consensus error! Delay " + str(delta) + " min", 'red')
            print colored("Lastest block time (utc) - " + str(block_time), 'green')
            print colored("Latest block height - " + str(block_height), 'green')
        else:
        	print colored("Consensus - OK", 'green')
        	print colored("Lastest block time (utc) - " + str(block_time), 'green')
        	print colored("Latest block height - " + str(block_height), 'green')



	# check if sufficient # of peers is available
    for i in url_net_info:
        url_data = json.load(urllib2.urlopen(i))
        foo = Info (url_data)
        if len(foo.info) < 5:
            print colored("Insufficient peers - under 5 peers available!  Current count " + str(len(foo.info)) + " peers", 'red')
        else:
        	print colored("Current number of peers - " + str(len(foo.info)), 'green')

	
	# get list of peer IP addresses from net_info
	peer_ip = []
	for k in foo.info:
		peer_ip.append(k['node_info']['listen_addr'])


	# check if all block heighs are in sync
	for i in url_dump:
		url_data = json.load(urllib2.urlopen(i))
		state = Dump (url_data)
        for k in peer_ip:
            # print state.dump[k]['Height']
            if state.dump[k]['Height'] != block_height+1:
                print colored("Block height different - " + k + ' ' + "(height " + str(state.dump[k]['Height'])+ ")", 'red')
            else:
                pass


	# scan all blocks
	start = block_height-2
	end = block_height+1
	url_block = []
    for number in range (start, end):
        block = 'http://35.204.86.158:46657/block?height=' + str(number)
        url_block.append(block)
    total_blocks = len(url_block) 
    
    class Block():
        def __init__(self, json):
            self.block=json["result"]["block"]["last_commit"]["precommits"]
    counts = dict()
    print ("Scanning all blocks...")
    for i in url_block:
        url_data = json.load(urllib2.urlopen(i))
        foo = Block (url_data)
        # print("Got " + i)
        for k in foo.block:
                try:
                    if k['validator_address']:
                        if k['validator_address'] not in counts:
                            counts[k['validator_address']] = 1    	                   
                        else:
                            counts[k['validator_address']] += 1 
                except:
                    pass
    for key, value in counts.items():
        participation = (value * 100) / total_blocks 
        print(key +" "+ str(participation) + '%')
status()


  























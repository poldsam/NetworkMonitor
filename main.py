import json
import urllib2
from datetime import datetime, date, timedelta
import os, time, httplib

url_status = [
    "http://35.204.86.158:46657/status", 
]

url_net_info = [
    "http://35.204.86.158:46657/net_info",
]

url_live = [
    "35.204.86.158:46657",
]


# Monitor if site is up and running
def site_running():
# while (True):
    for i in url_live:
        conn = httplib.HTTPConnection(i, timeout=10)
        try:
            conn.request("HEAD", "/")
            response = conn.getresponse()
            print i, response.status, response.reason
        except:
            print ("Cannot reach " + i)
            pass
        conn.close()
    # time.sleep(1000)
site_running()

# Number of peer nodes
def net_info():
    class Info():
        def __init__(self, json):
            self.info=json["result"]["peers"]
                
    for i in url_net_info:
        url_data = json.load(urllib2.urlopen(i))
        foo = Info (url_data)
        if len(foo.info) < 5:
            print ("Less than 5 peers! Current number of peers - " + str(len(foo.info)))
        else:
        	print ("Current number of peers - " + str(len(foo.info)))

net_info()  

# Block status and % of blocks committed by each validator
def status():
    class Status():
           def __init__(self, json):
            self.status=json["result"]
                
    for i in url_status:
        url_data = json.load(urllib2.urlopen(i))
        foo = Status (url_data)
        block_height =  foo.status['latest_block_height']
        block_time =  datetime.strptime(foo.status['latest_block_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if block_time < datetime.utcnow()-timedelta(seconds=120):
            print ("Late block - public consensus error!")
            print ("Latest block height " + str(block_height))
            print ("Lastest block time (utc) " + str(block_time))
        else:
        	print ("Consensus - OK")
        	print ("Latest block height - " + str(block_height))
        	print ("Lastest block time (utc) - " + str(block_time))

    	start = block_height-20
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
            #print counts
        for key, value in counts.items():
            participation = (value * 100) / total_blocks 
            print(key +" "+ str(participation) + '%')
status()


  























import json
import urllib2
import datetime
from datetime import datetime, date, timedelta
import os, time, httplib
from termcolor import colored
import time



url = [
    "35.192.48.94:46657",
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


for i in url:

    site_running(i)


    class Status:

        url_suffix = "/status"
        

        def __init__(self, url):
            self.url = url
 
        counter = 0 
        def get_block_height(self):
            self.counter +=1
            class Result():
                def __init__(self, json):
                    self.status=json["result"]

            url = self.url
            url_data = json.load(urllib2.urlopen("http://"+ i + self.url_suffix))
            result = Result (url_data)
            block_height =  result.status['latest_block_height']
            latest_block_time = result.status['latest_block_time']
            block_time =  datetime.strptime(latest_block_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            delta = datetime.utcnow() - block_time
            # print self.counter 
            if self.counter == 1:
                if block_time < datetime.utcnow() -timedelta(seconds=120):
                    print colored("Late block - public consensus error! Delay " + str(delta), 'red')
                    # print colored("Late block - public consensus error!",'red')
                    print colored("Latest block time (utc) - " + str(block_time), 'green')
                    print colored("Latest block height - " + str(block_height), 'green')
                    
                else:
                    print colored("Consensus - OK", 'green')
                    print colored("Lastest block time (utc) - " + str(block_time), 'green')
                    print colored("Latest block height - " + str(block_height), 'green')
            else: pass 
            
            return block_height 
   

    status = Status(i)
    status.get_block_height()

    class Net_Info(Status):

        url_suffix = "/net_info"

        def get_node_count(self):
            class Info():
                def __init__(self, json):
                    self.info=json["result"]["peers"]

            # url = self.url
            url_data = json.load(urllib2.urlopen("http://"+ i + self.url_suffix))
            peers = Info (url_data)
            count = len(peers.info)

            if count == 1:
                print colored("Insufficient nodes - under 5 nodes available!  Current count " + str(len(peers.info)) + " node", 'red')
            if 1 < count < 5:
                print colored("Insufficient nodes - under 5 nodes available!  Current count " + str(len(peers.info)) + " nodes", 'red')
            else:
                print colored("Current number of nodes - " + str(count), 'green')

            return count 

        def get_node_ip(self):
        # get peer node ip addresses 
            class Info():
                def __init__(self, json):
                    self.info=json["result"]["peers"]

            # url = self.url
            url_data = json.load(urllib2.urlopen("http://"+ i + self.url_suffix))
            peers = Info (url_data)

            node_ip = []
            for k in peers.info:
                node_ip.append(k['node_info']['listen_addr'])

            return node_ip 

    net_info = Net_Info(i)
    net_info.get_node_count()



    # # Check if all block heights are in sync
    class Dump_Consensus(Net_Info):

        url_suffix = "/dump_consensus_state"

        def __init__(self, url, node_ip):
            self.url = url 
            self.node_ip = node_ip

        def dump_consensus(self):
            #create class
            class Dump():
                def __init__(self, json):
                    self.dump=json["result"]["peer_round_states"]

            url = self.url
            url_data = json.load(urllib2.urlopen("http://"+ i + self.url_suffix))
            #get peer round states to check what validators think the block heigh should be
            peer_round_states = Dump (url_data)
            for k in self.node_ip:
                try:
                    # compare peer round states to actual block height for consensus
                    if peer_round_states.dump[k]['Height'] != block_height+1:
                        print colored("Block height different - " + k + ' ' + "(height " + str(peer_round_states.dump[k]['Height'])+ ")", 'red')
                    else:
                        pass
                except:
                    pass
                try:
                    if peer_round_states.dump["891023d33e161bafff356b74ea44730d295342b9"]['Height'] != block_height+1:
                        print colored("Block height different - " + ' ' + "(height " + str(peer_round_states.dump["891023d33e161bafff356b74ea44730d295342b9"]['Height'])+ ")", 'red')
                    else:
                        pass
                except:
                    pass


    consensus = Dump_Consensus(i, net_info.get_node_ip())
    consensus.dump_consensus()


    class Url_Block:

        last_run = 14
        url_suffix = "/block?height="

        def __init__ (self, url, block_height):
            self.url = url 
            self.block_height = block_height 


        def get_block_urls(self):

            if self.last_run <= self.block_height:
                start = self.last_run 
            else:
                start = self.block_height
            
            end = self.block_height + 1

            url_block = []
            for number in range (start, end):
                block = ("http://"+ i + self.url_suffix + str(number))
                url_block.append(block)

            return url_block    

    url_block = Url_Block(i, status.get_block_height())
    # url_block.get_block_urls()


    class Url_Validators(Url_Block):

        url_suffix = "/validators?height="

        def get_validators_urls(self):

            if self.last_run <= self.block_height:
                start = self.last_run 
            else:
                start = self.block_height
            
            end = self.block_height + 1

            url_validators = []
            for number in range (start, end):
                validators = ("http://"+ i + self.url_suffix + str(number))
                url_validators.append(validators)

            return url_validators     

    url_validators = Url_Validators(i, status.get_block_height())
    # url_validators.get_validators_urls()
            

    class Blockcount:

        def __init__(self, url, url_block):
            self.url = url
            self.url_block = url_block 


        #create classes
        class HeightByBlock():
            def __init__(self, json):
                self.heightbyblock=json["result"]["block"]


        # get validators at block height
        def get_blockcount(self):
            print colored ("Scanning all blocks...", 'green')

            total_blocks = len(self.url_block)
            # print total_blocks 
            blockcount = dict()
            for i in self.url_block:
                url_data = json.load(urllib2.urlopen(i))
                block = self.HeightByBlock (url_data)
                # print("Got " + i)
                for k in block.heightbyblock["last_commit"]["precommits"]:
                        try:
                            if k['validator_address']:
                                if k['validator_address'] not in blockcount:
                                    blockcount[k['validator_address']] = 1
                                else:
                                    blockcount[k['validator_address']] += 1
                        except:
                            pass

            self.participation(blockcount)
            return blockcount 

        # get validators at block height
        def get_block_validators(self):

            total_blocks = len(self.url_block)
            block_validators_list = dict()
            for i in self.url_block:
                url_data = json.load(urllib2.urlopen(i))
                block = self.HeightByBlock (url_data)
                block_height_at = block.heightbyblock['header']['height']
                block_validators = []
                # print("Got " + i)
                for k in block.heightbyblock["last_commit"]["precommits"]:
                        try:
                            if k['validator_address']:
                                block_validators.append(k['validator_address'])
                        except:
                            pass

                block_validators_list[block_height_at] = block_validators
            return block_validators_list
                                

        def participation(self, blockcount):

            for key, value in blockcount.items():
                participation = (value * 100) / len(self.url_block)
                print(key +" "+ str(participation) + '%')

    blockcount = Blockcount(url, url_block.get_block_urls())
    # blockcount.get_blockcount()
    # blockcount.get_block_validators()
    # blockcount.participation(blockcount)


    class Validatorscount:

        def __init__(self, url, url_validators, blockcount, block_validators_list):
            self.url = url
            self.url_validators = url_validators 
            self.blockcount = blockcount
            self.block_validators_list = block_validators_list


        #create classes
        class ValidatorsHeight():
            def __init__(self, json):
                self.validatorsheight=json["result"]



        # get validators at validators height
        def get_validatorscount(self):

            print colored ("Calculating uptime...", 'green')

            total_val_blocks = len(self.url_validators)
            validatorscount = dict()
            # validator_validators_list = dict()
            for i in self.url_validators:
                url_data = json.load(urllib2.urlopen(i))
                result = self.ValidatorsHeight (url_data) 
                # print("Got " + i)
                for k in result.validatorsheight['validators']:
                    try:
                        if k['address']:
                            if k['address'] not in validatorscount:
                                validatorscount[k['address']] = 1
                            else:
                                validatorscount[k['address']] += 1  
                    except:
                        pass

            self.uptime(validatorscount)
            return validatorscount 

        # get validators at validators height
        def get_validators_validators(self):

            total_val_blocks = len(self.url_validators)
            validator_validators_list = dict()
            for i in self.url_validators:
                url_data = json.load(urllib2.urlopen(i))
                result = self.ValidatorsHeight (url_data)
                validators_block_height_at = result.validatorsheight['block_height']
                validator_validators = [] 
                # print("Got " + i)
                for k in result.validatorsheight['validators']:
                    try:
                        if k['address']:
                            validator_validators.append(k['address']) 
                    except:
                        pass
                validator_validators_list[validators_block_height_at] = validator_validators

            self.consecutive_blocks(validator_validators_list, validator_validators)
            return validator_validators_list, validator_validators 


        # calculate uptime for each validator 
        def uptime(self, validatorscount):
            # print self.blockcount
            for key in self.blockcount:
                expected = validatorscount[key]
                actual = self.blockcount[key]
                uptime = (actual * 100) / expected
                print(key +" "+ str(uptime) + '%')


        def consecutive_blocks(self, validator_validators_list, validator_validators):
        # difference between expected and actual block validators by block 
            delta = {}
            for key in self.block_validators_list:
                delta[key] = list(set(validator_validators_list[key]) - set(self.block_validators_list.get(key, [])))

            # print delta 

            for n in validator_validators:
                # print n 
                if any (n in val for val in delta.values()):
                    # get keys with missing values
                    keys = [key for key, value in delta.items() if n in value]
                    # check if 3 entries are consecutive
                    subs = [keys[i:i+3] for i in range(len(keys)) if len(keys[i:i+3]) == 3]
                    if len(keys) > 2:
                        print colored(n + " has missed three consecutive blocks " + str(subs[0]), 'red')
                        # print colored(subs[0], 'red')
                        print "Total blocks missed " + str(keys)


    validatorscount = Validatorscount(i, url_validators.get_validators_urls(), blockcount.get_blockcount(), blockcount.get_block_validators())
    validatorscount.get_validatorscount()
    validatorscount.get_validators_validators()

    print '\n'









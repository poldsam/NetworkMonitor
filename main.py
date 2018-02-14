import json
import urllib2
from datetime import datetime, date, timedelta
import os, time, httplib

# Monitor block time
def status():
	class Status():
    	   def __init__(self, json):
        	self.status=json["result"]
                
	url = "http://35.204.86.158:46657/status"
	url_data = json.load(urllib2.urlopen(url))
	foo = Status (url_data)
	block_height =  foo.status['latest_block_height']
	block_time =  datetime.strptime(foo.status['latest_block_time'], '%Y-%m-%dT%H:%M:%S.%fZ')

	if block_time < datetime.utcnow()-timedelta(seconds=120):
	    print "Late block - public consensus error!"
status()


# Monitor peers
def net_info():
    class Info():
        def __init__(self, json):
            self.info=json["result"]["peers"]
                
    url = "http://35.204.86.158:46657/net_info"
    url_data = json.load(urllib2.urlopen(url))
    foo = Info (url_data)
    if len(foo.info) < 20:
    	print "Insufficient peers!"
net_info()    


# Monitor if site can be reached
sites = [
	"www.google.com",
	"35.204.86.158:46657",
	"127.0.0.1:8000",
]

while (True):
	for i in sites:
		conn = httplib.HTTPConnection(i, timeout=10)
		try:
			conn.request("HEAD", "/")
			response = conn.getresponse()
			print i, response.status, response.reason
		except:
			print "Cannot reach" + ' ' + i 
			pass
		conn.close()
	time.sleep(20)

	
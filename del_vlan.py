#!/usr/bin/python3

import os, time, signal, sys, socket, requests, json

interval = 3
host = socket.gethostname()
webhook_url = 'https://hooks.slack.com/services/XXXXX/XXXXXX/XXXXXXXXXXX'

#Trap Ctr+C
def signal_handler(sig, frame):
        print('Stoped!')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

#RX and TX package collector.
def get_packets(iface, line):
        with open('/sys/class/net/' +
            iface + '/statistics/' +
            line + '_packets', 'r') as f:
            data = f.read(); f.close()
            return int(data)

#Slackhook
def slack_hook():
    slack_data = {"channel": "#nethooks",
      "attachments": [
        {
          "text": "WARN: "+str(host)+" inactive VLAN",
          "color": "#FF0000",
          "mrkdwn_in": ["text"],
          "fields": [
           { "title": "HOST:", "value": host, "short": "true" },
           { "title": "Removed Interface:", "value": f'{del_vlan}', "short": "true" }
          ]
        }
      ]
    }

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise ValueError(f'Error CODE:{response.status_code}, response is:{response.text}')

inDB = {}
outDB = {}
int_face = os.listdir('/sys/class/net/')
#GET interface list, and collect packages.
for interface in int_face:
    if (interface == 'lo' or interface == interface.split(".")[0] 
    or interface == interface.split(".")[0]+str(".500")
    or interface == interface.split(".")[0]+str(".3400")
    or interface == interface.split(".")[0]+str(".3401")):
        continue
    else:
        rx = get_packets(interface, 'rx')
        inDB[interface] = rx
        inDB2 = inDB.copy()
time.sleep(interval)

#Drop from main dict, the interface which has traffic on it.
for interface in inDB2:
    rx = get_packets(interface, 'rx')
    if (rx != inDB[interface]):
        inDB.pop(interface)

#Check 5 times * $interval_time, condition for vlan remove.

iDB = {}
x = 0
if len(inDB) == 0:
    print('All Interfaces are active!'); exit()
while x < 5:
    for inets in inDB:
        time.sleep(interval)
        x = x+1
        rx = get_packets(inets, 'rx')
        iDB[inets] = rx
        if ( rx == inDB[inets] and x == 5 ):
            for del_vlan in inDB:
                #expect arp-proxy replay
                commandA = '/sbin/arping 1.1.1.1 -c 1 -I'+str(del_vlan)
                exit = os.WEXITSTATUS(os.system(commandA))
                if exit != 0:
                    os.system("/sbin/vconfig rem "+str(del_vlan))
                    slack_hook()



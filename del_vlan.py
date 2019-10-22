#!/usr/bin/python3

import os, time, signal, sys, socket, requests, json

interval = 1
host = socket.gethostname()
webhook_url = 'https://hooks.slack.com/services/XXXXXXX/XXXXXXX/XXXXXXXX'

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
        tx = get_packets(interface, 'tx')
        inDB[interface] = rx; outDB[interface] = tx
        inDB2 = inDB.copy(); outDB2 = outDB.copy()
time.sleep(interval)

#Drop from main dict, the interface which has traffic on it.
for interface in inDB2:
    rx = get_packets(interface, 'rx')
    tx = get_packets(interface, 'tx')
    if (rx != inDB[interface] or tx != outDB[interface]):
        inDB.pop(interface); outDB.pop(interface)

#Check 5 times * $interval_time, condition for vlan remove.

oDB = {}
iDB = {}
x = 0
if len(inDB) == 0:
    print('All Interfaces are active!'); exit()
while x < 5:
    for inets in inDB:
        x = x+1
        rx = get_packets(inets, 'rx')
        tx = get_packets(inets, 'tx')
        iDB[inets] = rx; oDB[inets] = tx
        if ( rx == iDB[inets] and tx == oDB[inets] 
            and rx == inDB[inets] and tx == outDB[inets]
            and x == 5 ):
            for del_vlan in inDB:
                commandA = '/sbin/arping 1.1.1.1 -c 1 -I'+str(del_vlan)
                exit = os.WEXITSTATUS(os.system(commandA))
                if exit != 0:
                    os.system("/sbin/vconfig rem "+str(del_vlan))
                    slack_hook()
        time.sleep(interval)



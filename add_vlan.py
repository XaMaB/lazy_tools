#!/usr/bin/python3

import glob, os, subprocess, socket, requests, json

#GET vlans, that router send us.
path = '/tmp/rc-*'
control_vlans = []
if glob.glob(path):
    for r_file in glob.glob(path):
       clients_vlans = set([x.split('\t')[2].rstrip() for x in open(r_file).readlines()])
       for vlans_id in clients_vlans:
           control_vlans.append(vlans_id)

#GET configured interface list.
int_face = os.listdir('/sys/class/net/')
conf_vlans = []; phys = set([])
for interface in int_face:
    vlans_cur  = interface.split(".")
    for items in vlans_cur:
        if (items == interface.split(".")[0] and interface.split(".")[0] != 'lo') :
            phys.add(interface.split(".")[0])
        else:
            if items != interface.split(".")[0]:
                conf_vlans.append(items)

#Slackhook
host = socket.gethostname()
webhook_url = 'https://hooks.slack.com/services/XXXX/XXXX/XXXX'

def slack_hook():
    slack_data = {"channel": "#nethooks",
      "attachments": [
        {
          "text": "INFO: "+str(host)+" NEW VLAN",
          "color": "#008000",
          "mrkdwn_in": ["text"],
          "fields": [
           { "title": "HOST:", "value": host, "short": "true" },
           { "title": "New VLAN added:", "value": f'{phys_int}.{tag}', "short": "true" }
          ]
        }
      ]
    }

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise ValueError(f'Error CODE:{response.status_code}, response is:{response.text}')

#func to get vlans tags with tcpdump
dumped_vlans = []
def listen(INTF):
    dumped_tags = subprocess.getoutput("/usr/bin/timeout 5s /usr/sbin/tcpdump -i " + INTF + 
    " -nn -e vlan 2>/dev/null | /usr/bin/awk '!seen[$11] {print substr($11, 1, length($11)-1)} {++seen[$11]}'")
    raw_list = dumped_tags.split("\n")
    for tags in raw_list:
        if tags.isdigit():
            dumped_vlans.append(tags)
#Compare 2 lists (if control vlans is configured).
unconf_vlan_r = []
for unconf in control_vlans:
    if unconf not in conf_vlans:
        unconf_vlan_r.append(unconf)
        unconf_vlan = set(unconf_vlan_r)

#listen phys interface if new clients on unconfigured vlans.
if len(unconf_vlan) != 0:
    for phys_int in phys:
        listen(phys_int)
        for tag in unconf_vlan:
            if tag in dumped_vlans:
                os.system("/sbin/vconfig add "+str(phys_int)+" "+str(tag))
                os.system("/usr/sbin/ip link set up dev "+str(phys_int)+"."+str(tag))
                slack_hook()



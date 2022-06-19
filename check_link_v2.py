#!/usr/bin/python3

import time, signal, sys, json, requests, socket

#globVars

iface = "eth0"
interval = 2

#webhook_url = 'https://hooks.slack.com/services/XXXX/XXXXX/XXXXXX'

host = socket.gethostname()

class bcolors:
    RED     = "\033[1;31m"
    BLUE    = "\033[1;34m"
    CYAN    = "\033[1;36m"
    GREEN   = "\033[0;32m"
    RESET   = "\033[0;0m"
    BOLD    = "\033[;1m"
    REVERSE = "\033[;7m"
    ENDC    = '\033[0m'

def signal_handler(sig, frame):
        print('Stoped!')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


def get_bytes(line):
    with open('/sys/class/net/' + 
         iface + '/statistics/' + 
         line + '_bytes', 'r') as f:
        data = f.read();
        return int(data)

def change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return int(0)

def slack_hook():
    slack_data = {
      "attachments": [
        {
          "text": "WARN: "+str(host)+" Network DROP",
          "color": "#FF0000",
          "mrkdwn_in": ["text"],
          "fields": [
           { "title": "HOST:", "value": host, "short": "true" },
           { "title": "Bandwidth 5sec ago:", "value": f'{bfbw}Mbps', "short": "true" },
           { "title": "Difference:", "value": f'{differ}%', "short": "true" },
           { "title": "Bandwidth current:", "value": f'{nowbw}Mbps', "short": "true" }
          ]
        }
      ]
    }

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise ValueError(f'Error CODE:{response.status_code}, response is:{response.text}')

tx_speed = 0; tx_speedl = 0
rx_speed = 0; rx_speedl = 0

while(True):
    tx1 = get_bytes('tx')
    rx1 = get_bytes('rx')

    tx_speedl = tx_speed
    rx_speedl = rx_speed

    time.sleep(interval)

    tx2 = get_bytes('tx')
    rx2 = get_bytes('rx')

    tx_speed = round((((tx2 - tx1) * 8) / 1000000) / interval, 2)
    rx_speed = round((((rx2 - rx1) * 8) / 1000000) / interval, 2)

    diff_tx = round(change( tx_speed, tx_speedl ))
    diff_rx = round(change( rx_speed, rx_speedl ))

    print( f'TX: {bcolors.GREEN}{tx_speed}{bcolors.ENDC} Mbps | tx_diff: {bcolors.RED}{diff_tx}{bcolors.ENDC} % | RX: {bcolors.GREEN}{rx_speed}{bcolors.ENDC} Mbps | rx_diff: {bcolors.RED}{diff_rx}{bcolors.ENDC} %', end='\n', flush=False )
#    if diff_tx > 100:
#       bfbw = tx_speedl; nowbw = tx_speed; differ = diff_tx
#       slack_hook()
#    if diff_rx > 100:
#       bfbw = rx_speedl; nowbw = rx_speed; differ = diff_rx
#       slack_hook()


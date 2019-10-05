#!/usr/bin/python3

import time, signal, sys, json, requests

#globVars
iface = "eth0"
interval = 3
webhook_url = 'https://hooks.slack.com/services/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'

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

def slack_hook():
    slack_data = {
      "attachments": [
        {
          "text": str(rx_speed)+" Mbps",
          "color": "#FF0000",
          "mrkdwn_in": ["text"],
          "fields": [
        { "title": "Prober", "value": "MONIT_HOST", "short": "true" },
          ]
        }
      ]
    }

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise ValueError(f'Request to slack returned an error {response.status_code}, the response is:{response.text}')


while(True):
    tx1 = get_bytes('tx')
    rx1 = get_bytes('rx')

    time.sleep(interval)

    tx2 = get_bytes('tx')
    rx2 = get_bytes('rx')

    tx_speed = round((((tx2 - tx1) * 8) / 1000000) / interval, 2)
    rx_speed = round((((rx2 - rx1) * 8) / 1000000) / interval, 2)

    print(f'RX: {rx_speed} Mbps | TX: {tx_speed} Mbps')
    if rx_speed > 10:
        slack_hook()


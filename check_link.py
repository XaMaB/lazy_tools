#!/usr/bin/python3

import time, signal, sys, json, requests

#globVars
iface = "eth0"
interval = 2
webhook_url = 'https://hooks.slack.com/services/XXXX/XXXXX/XXXXXX'

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

    print(f'TX: {tx_speed} Mbps | tx_diff: {diff_tx}% | RX: {rx_speed} Mbps | rx_diff: {diff_rx}', end='\r', flush=True )



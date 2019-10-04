#!/usr/bin/python3

import time, signal, sys

iface = "eth0.25"
interval = 3

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

while(True):
    tx1 = get_bytes('tx')
    rx1 = get_bytes('rx')

    time.sleep(interval)

    tx2 = get_bytes('tx')
    rx2 = get_bytes('rx')

    tx_speed = round((((tx2 - tx1) * 8) / 1000000) / interval, 2)
    rx_speed = round((((rx2 - rx1) * 8) / 1000000) / interval, 2)

    print(f"RX: {rx_speed} Mbps | TX: {tx_speed} Mbps")



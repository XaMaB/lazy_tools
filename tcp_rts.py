#!/usr/bin/env python3

import time, signal, sys, json, requests, socket, subprocess

interval = 2

host = socket.gethostname()

def signal_handler(sig, frame):
        print('Stoped!')
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def change(current, previous):
    if current == previous:
        return 0
    try:
        return round((current - previous) / interval )
    except ZeroDivisionError:
        return int(0)

def netstat_rts(key):
    keys = []; values = []
    f = open('/proc/net/netstat')
    lines = f.readlines();f.close()
    for i in lines[0].split():
        if i == 'TcpExt:':
            continue
        else:
            keys.append(i)
    for i in lines[1].split():
        if i == 'TcpExt:':
            continue
        else:
            values.append(i)
    tcps = dict(zip(keys, values))
    return int(tcps[key])

def segmetn_sent():
    segmetn_out = subprocess.getoutput("/bin/netstat -s |grep 'segments send out' | /usr/bin/awk '{print $1}'")
    return int(segmetn_out)

while(True):
    s_prv = segmetn_sent()
    prv = netstat_rts('TCPFastRetrans')

    time.sleep(interval)

    s_curr = segmetn_sent()
    curr = netstat_rts('TCPFastRetrans')

    send_sec = change(s_curr, s_prv)
    retransm = change(curr, prv)

    bandw = round(((( send_sec * 1460 ) * 8) / 1000000), 2)
    losses = round((( retransm / send_sec) * 100), 2)

    print(f'bw: {bandw}Mbps |  segm: {send_sec} | retr: {retransm} | %loss: {losses}')





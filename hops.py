
# !/usr/bin/env python
from __future__ import print_function

import socket
import os
import sys
import struct
import time
import statistics

ICMP_ECHO_REQUEST = 8

DESTINATION_REACHED = 1
SOCKET_TIMEOUT = 2


def checksum(str_):
    str_ = bytearray(str_)
    csum = 0
    countTo = (len(str_) // 2) * 2

    for count in range(0, countTo, 2):
        thisVal = str_[count +1] * 256 + str_[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff

    if countTo < len(str_):
        csum = csum + str_[-1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
    startTime = time.time()

    while (startTime + timeout - time.time()) > 0:
        try:
            recPacket, (addr, x) = mySocket.recvfrom(1024)
        except socket.timeout:
            break  # timed out
        timeReceived = time.time()

        # Fetch the ICMPHeader fromt the IP
        icmpHeader = recPacket[20:28]

        icmpType, code, checksum, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader)

        if icmpType == 11 and code == 0:
            return (timeReceived - startTime, addr, None)
        elif icmpType == 0 and code == 0:
            return (timeReceived - startTime, addr, DESTINATION_REACHED)

    return (None, None, SOCKET_TIMEOUT)


def sendOnePing(mySocket, destAddr, ID):

    # Make a dummy header with a 0 checksum
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    header = struct.pack("bbHHh",
                         ICMP_ECHO_REQUEST,  # type (byte)
                         0,                  # code (byte)
                         0,                  # checksum (halfword, 2 bytes)
                         ID,                 # ID (halfword)
                         1)                  # sequence (halfword)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # htons: Convert 16-bit integers from host to network  byte order
        myChecksum = socket.htons(myChecksum) & 0xffff
    else:
        myChecksum = socket.htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    # AF_INET address must be tuple, not str
    mySocket.sendto(packet, (destAddr, 1))


def doOnePing(destAddr, timeout, ttl):
    icmp = socket.getprotobyname("icmp")
    # SOCK_RAW is a powerful socket type. For more details:
    # http://sock-raw.org/papers/sock_raw

    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    if(ttl>0):
        mySocket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    mySocket.settimeout(timeout)

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay, address, notify = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return (delay, address, notify)


def print_part(delay, address, prevaddr):
    if not delay:
        #print('*', end=' ', flush=True)
        #print('*')
        return

    delay *= 1000
    if not prevaddr == address:
        try:
            host, _, _ = socket.gethostbyaddr(address)
        except:
            host = address
        #print('{} ({})  {:.3f} ms'.format(host, address, delay))
        #return(address)
       #,      end=' ', flush=True)
    #else:
        #print(' {:.3f} ms'.format(delay))
             #, end=' ', flush=True)

# TRACEROUTE DESTINATION -----------------------------------------------
def traceroute(host, timeout, maxHops):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is
    # lost
    dest = socket.gethostbyname(host)
    schops=[]
    previouslist=["a"]
    for ttl in range(1, maxHops +1):
        delay, address, info = doOnePing(dest, timeout, ttl)
        if(address != 'None'):
            schops.append(address)
        #print(schops)
        #if previouslist != schops:
        #    previouslist = schops
        #else:
        #    break
        if info == DESTINATION_REACHED:
            break
    
    if(ttl >  (maxHops)):
            ttl =(-1)
            print("Max hops reached")
    return(ttl, schops)
    

# PING DESTINATION ----------------------------------------------------
def verbose_ping(host, timeout=5, count=4):
    dest = socket.gethostbyname(host)
    delay_list = []
    for i in range(1,count):
        try:
            delay, address, notify = doOnePing(dest, timeout, 0)
        except socket.gaierror:
            print("ping failed (socket error)")
            break

        if delay == None:
            print("ping failed (timeout wihtin %ssec.)" % timeout)
        else:
            delay = delay*1000
            delay_list.append(delay)
    return(statistics.mean(delay_list))

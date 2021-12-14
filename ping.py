import os
import socket
import sys
import hops
import time
from subprocess import STDOUT
import subprocess, re
import pandas as pd
from time import gmtime, strftime

if __name__ == "__main__":

    destination = "192.168.248.169"
    count = 0
    command = ["ping", "-c", "3","-s", "64", "-i", "0.2", "-w", "0.2", destination]
    exists = os.path.isfile('enb_ping.csv')
    if(exists == True):
        dataF =  pd.read_csv("enb_ping.csv")
    else:
        dataF = pd.DataFrame(columns=['id','Destination','Datetime','avgrtt','loss'])

    timeout = 300
    starttime=time.time()
    
    while time.time() < (starttime + timeout):
        try:
            ping = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            [out, err] = ping.communicate()
            if ping.returncode == 0:
                avgRTT = re.search("rtt min/avg/max/mdev = (\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)", str(out)).group(1)
                loss=re.search("(\d+)% packet loss", str(out)).group(0)
                #print(str(sys.argv[1]), ", average rtt:  %s" %avgRTT ," loss", loss)

                sysTime = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                dataF = dataF.append({'id':str(sys.argv[1]),'Destination': destination,'Datetime': sysTime, 'avgrtt': avgRTT, 'loss': str(loss)}, ignore_index=True)
        except subprocess.TimeoutExpired:
            ping.kill()
        time.sleep(0.001)
        count += 1
        dataF.to_csv('enb_ping.csv',index= False)

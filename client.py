#!/usr/bin/env python
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.sendto("uptime|human", ('255.255.255.255', 53005))
msg,client = s.recvfrom(1024)
print "msg =",msg
print "client =",client
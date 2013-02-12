#!/usr/bin/env python

# Import our database class to make things nice
from db import DB

# Networking stuff
import select, socket

from calls import CallManager

# Start up and initialize our database
db = DB()
db.init()

d = db.insert("hosts", date="hi",host="fuck")

#print "new row id:",db.id

info = db['*|hosts|id=%d'%(db.id)]
print "info =",info
print "id of record:",db.id

#db.delete("hosts")

# Terminate database connection (cheeky?)
del db

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('<broadcast>', 53005))
s.setblocking(0)

cm = CallManager(s)

while True:
	try:
		result = select.select([s], [], [])
	except KeyboardInterrupt:
		break

	msg,client = result[0][0].recvfrom(1024)

	cm.client(result[0][0], client)
	cm.process_call(msg)
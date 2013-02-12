from datetime import timedelta

import socket
import sys

class Calls(object):
	def hostname(self, args=None):
		return socket.gethostname()

	def uptime(self, args=None):
		fp = open("/proc/uptime", "r")
		time = fp.readline().split()[0]

		if args == "human":
			time = float(time)
			return str(timedelta(seconds = time))
		else:
			s,ms = time.split(".")
			return "%s s, %s ms" % (s, ms)

class CallManager(Calls):
	def __init__(self, srv_sock):
		self.s = srv_sock
		self.c = None
		self.cs = None

	def client(self, c_sock, c_info):
		self.c = c_info
		self.cs = c_sock

	def send(self, msg):
		if self.c is None or self.cs is None:
			raise Exception("No client connection was passed to client()")

		self.cs.sendto(msg, self.c)

	def process_call(self, msg, delim="|"):
		if msg.find(delim) != -1:
			cmd,args = msg.split(delim, 1)
		else:
			cmd = msg
			args = None

		ret = ""

		try:
			if hasattr(self.__class__, cmd) and callable(getattr(self.__class__, cmd)):
				ret = getattr(self, cmd)(args)
		except:
			pass

		self.send(ret)
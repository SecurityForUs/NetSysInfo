from datetime import timedelta

import socket
import sys
import os
import subprocess
import re

class Calls(object):
	def sanitize(self, args):
		if args is None:
			return None

		invalid = [';', '&', '>']

		for char in invalid:
			args = args.replace(char, "")

		return args

	"""
	Formats data into a perf data-valid string, for use in Nagios or anything else that collects such data.
	Rturns "" on error.
	"""
	def format_perf(self, label, value, uom="", warn=None, crit=None, minv=None, maxv=None):
		label = str(label)

		perf = ""

		if (len(label) > 19) or (label.find("=") != -1) or (label.find("'") != -1) or (label.endswith("'") is False) or (label.startswith("'") is False):
			return ""

		reg_vmm = re.compile("([^\-0-9\.])")

		perf = "'%s'=%s" % (label, str(value))

		reg_uom = re.compile("([^s%Bc])")

		if uom != "" and reg_uom.match(uom) != None:
			return ""

		perf = "%s;" % (uom)

		if warn != None and reg_vmm.match(warn) != None:
			return ""

		if minv != None and reg_vmm.match(minv) != None:
			return ""

		if maxv != None and reg_vmm.match(maxv) != None:
			return ""

		perf = "'%s'=%s;%s;%s;%s;%s;%s" % (str(label), str(value), str(uom),  str(warn), str(crit), str(minv), str(maxv))

		return perf
		
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

	def adapter(self, args=None):
		if args == "list":
			a = ""

			for adap in os.listdir("/sys/class/net"):
				a = "%s %s" % (a, adap)

			return a

		try:
			adap,res = args.split("|")
		except:
			return -1

		if res == "info":
			a = ""

			for types in os.listdir("/sys/class/net/%s" % (adap)):
				a = "%s %s" % (a, types)

			return a

		fp = open("/sys/class/net/%s/statistics/%s" % (adap, res), "r")
		return fp.readline().strip()

	def ports(self, args=None):
		if args == "used":
			args = "-ntlu | grep \":\" | sed 's/:::/:/' | awk '{printf \"%s/%s\\n\", $4, $1}' | awk -F: '{print $2}' | tr '\\n' ' '"
		else:
			args = "-ntlup | grep \""+args+"\" | grep \":\" | sed 's/:::/:/' | awk '{printf \"%s/%s\\n\", $4, $1}' | awk -F: '{print $2}' | tr '\\n' ' '"

		out = subprocess.check_output("netstat %s" % (args), shell=True)

		return out

	def uname(self, args=None):
		if args is None:
			args = ""
		else:
			args = self.sanitize(args)

		out = subprocess.check_output("uname %s" % (args), shell=True)

		return out.rstrip()

	def loadavg(self, args=None):
		args = self.sanitize(args)

		load = os.getloadavg()

		if args == "1":
			return str(load[0])
		elif args == "5":
			return str(load[1])
		elif args == "15":
			return str(load[2])
		else:
			return "%s/1min %s/5min %s/15min" % (load[0], load[1], load[2])

	"""
	Default output:
	MemTotal MemFree SwapCached SwapTotal SwapFree
	"""
	def mem(self, args=None):
		args = self.sanitize(args)

		print "args:",args

		if args is None:
			args = "^Mem\\|^Swap"
			
		out = subprocess.check_output("cat /proc/meminfo | grep \""+args+"\" | awk '{print $2}' | tr '\\n' ' '", shell=True)

		return out

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

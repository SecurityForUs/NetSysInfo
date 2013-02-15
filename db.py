# We use sqlite for our backend
import sqlite3

class DB(object):
	"""
	Create a connection and cursor to the database
	"""
	def __init__(self, db="test"):
		self.conn = sqlite3.connect("%s.db" % (db))
		self.c = self.conn.cursor()
		self.rowid = -1

	@property
	def id(self):
		return self.rowid

	"""
	Initialize database by creating tables then commit.  If tables already exist, just ignore the raise
	"""
	def init(self):
		try:
			self.c.execute("CREATE TABLE hosts (id integer primary key autoincrement, date text, host text, ip text, last_send text, last_recv text)")
			self.c.execute("CREATE TABLE requests (id integer primary key autoincrement, date text, host integer, msg_sent text, msg_recv text)")
			self.conn.commit()
		except sqlite3.OperationalError:
			pass

	def insert(self, tbl, **kwargs):
		q = ""
		cols = ""
		vals = ()
		data = kwargs

		for key, val in data.iteritems():
			if q == "":
				q = "?"
				cols = key
			else:
				q = "%s,?" % (q)
				cols = "%s,%s" % (cols, key)

			vals += (val,)

		try:
			self.c.execute("INSERT INTO '%s'(%s) VALUES(%s)" % (tbl, cols, q), vals)
			self.rowid = self.c.lastrowid
			self.conn.commit()

			return self.rowid
		except:
			return 0

	def delete(self, tbl, crit = None):
		if crit is not None:
			self.c.execute("DELETE FROM %s WHERE %s" % (tbl, crit))
		else:
			self.c.execute("DELETE FROM %s" % (tbl))

		self.conn.commit()

	"""
	Cheeky way to close the connection, but seems to work without issues.
	"""
	def __del__(self):
		self.conn.close()

	def select(self, rows, table, crit=""):
		q = "SELECT %s FROM %s" % (rows, table)

		if crit is not "":
			q = "%s WHERE %s" % (q, crit)

		self.c.execute(q)
		self.row = self.c.fetchone()

	# Apparently del doesn't call __del__ immediately all the time, this is kind of a hack to work with that
	def close(self):
		self.__del__()

	def __getitem__(self, key):
		parts = key.split("|")
		rows = parts[0]
		tbl = parts[1]
		crit = ""

		try:
			crit = parts[2]
		except:
			pass

		if "id" not in rows:
			rows = "id,%s" % (rows)

		self.select(rows, tbl, crit)

		return self.row
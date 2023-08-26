from Job import Job

import re, ipaddress

class Abusers(Job) :

	def __init__(self, redis_host=None, copy_cache=False) :
		name = "abusers"
		data = ["https://iplists.firehol.org/files/firehol_abusers_30d.netset"]
		filename = "abusers.list"
		type = "line"
		regex = r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/?[0-9]*$"
		redis_ex = 86400
		super().__init__(name, data, filename, redis_host=redis_host, redis_ex=redis_ex, type=type, regex=regex, copy_cache=copy_cache)

	def _edit(self, chunk):
		if self._redis != None:
			network = chunk.decode("utf-8")
			if re.match(network, r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\/?[0-9]+$"):
				ips = [str(ip).encode("utf-8") for ip in ipaddress.IPv4Network(network)]
		return [chunk]


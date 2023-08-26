#!/usr/bin/python3

import os, socket, sys, stat

VALIDATION = os.getenv("CERTBOT_VALIDATION", None)
TOKEN = os.getenv("CERTBOT_TOKEN", None)
if VALIDATION is None or TOKEN is None:
	sys.exit(1)

try:
	with open(f"/opt/bunkerized-nginx/acme-challenge/.well-known/acme-challenge/{TOKEN}", "w") as f:
		f.write(VALIDATION)
except :
	sys.exit(2)

try :
	if os.path.exists("/tmp/autoconf.sock") and stat.S_ISSOCK(os.stat("/tmp/autoconf.sock").st_mode) :
		sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		sock.connect("/tmp/autoconf.sock")
		sock.sendall(b"acme")
		data = sock.recv(512)
		if data != b"ok" :
			raise Exception("can't acme")
		sock.sendall(b"close")
except :
	sys.exit(3)

sys.exit(0)

#!/usr/bin/python3

import os, sys

TOKEN = os.getenv("CERTBOT_TOKEN", None)
if TOKEN is None:
	sys.exit(1)

try:
	os.remove(
		f"/opt/bunkerized-nginx/acme-challenge/.well-known/acme-challenge/{TOKEN}"
	)
except :
	sys.exit(2)

sys.exit(0)

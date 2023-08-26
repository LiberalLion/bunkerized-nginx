from Job import Job

from logger import log

class CertbotNew(Job) :

	def __init__(self, redis_host=None, copy_cache=False, domain="", email="", staging=False) :
		name = "certbot-new"
		data = ["certbot", "certonly", "--manual", "--preferred-challenges=http", "--manual-auth-hook", "/opt/bunkerized-nginx/jobs/certbot-auth.py", "--manual-cleanup-hook", "/opt/bunkerized-nginx/jobs/certbot-cleanup.py", "-n", "-d", domain, "--email", email, "--agree-tos"]
		if staging :
			data.append("--staging")
		type = "exec"
		self.__domain = domain
		super().__init__(name, data, filename=None, redis_host=redis_host, type=type, copy_cache=copy_cache)

	def _callback(self, success):
		if success:
			log(
				"certbot-new",
				"INFO",
				f"generated certificate for domain(s) {self.__domain}",
			)
		else:
			log(
				"certbot-new",
				"ERROR",
				f"can't generate certificate for domain(s) {self.__domain}",
			)


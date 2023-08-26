import socketserver, threading, os, stat

from logger import log

class ReloadServerHandler(socketserver.BaseRequestHandler):

	def handle(self):
		locked = False
		try:

			while True:
				data = self.request.recv(512)
				if not data or data not in [b"lock", b"reload", b"unlock", b"acme"]:
					break
				if data == b"lock":
					self.server.controller.lock.acquire()
					locked = True
					self.request.sendall(b"ok")
				elif data == b"unlock" :
					self.server.controller.lock.release()
					locked = False
					self.request.sendall(b"ok")
				elif data == b"acme":
					if ret := self.server.controller.send(files="acme"):
						self.request.sendall(b"ok")
					else:
						self.request.sendall(b"ko")
				elif data == b"reload":
					if ret := self.server.controller.reload():
						self.request.sendall(b"ok")
					else:
						self.request.sendall(b"ko")
		except Exception as e:
			log("RELOADSERVER", "ERROR", f"exception : {str(e)}")
		if locked :
			self.server.controller.lock.release()

class ThreadingUnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer) :
	pass

def run_reload_server(controller) :
	server = ThreadingUnixServer("/tmp/autoconf.sock", ReloadServerHandler)
	os.chown("/tmp/autoconf.sock", 0, 101)
	os.chmod("/tmp/autoconf.sock", 0o770)
	server.controller = controller
	thread = threading.Thread(target=server.serve_forever)
	thread.daemon = True
	thread.start()
	return (server, thread)

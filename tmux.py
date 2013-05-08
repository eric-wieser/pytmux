import subprocess

class Tmux(object):
	def __init__(self, socket = None, use256Colors = True):
		self.socket = socket
		self.use256Colors = use256Colors

	@property
	def baseCommand(self):
		command = ['tmux']
		if self.socket is not None:
			command += ['-S', self.socket]
		if self.use256Colors is not None:
			command += ['-2']

		return command

	def execute(self, cmd):
		print self.baseCommand + cmd
		subprocess.call(self.baseCommand + cmd)
		return self

	def _startSession(self, session, window, command):
		self.execute(['new-session', '-ds', session.name, '-n', window.name, command])

	def session(self, name, attach = False, command = None):
		return Session(self, name)

class Session(object):
	def __init__(self, tmux, name):
		self.name = name
		self.tmux = tmux
		self.running = False

	def window(self, name):
		return Window(self, name)

	def _startWindow(self, window, command):
		if not self.running:
			self.tmux._startSession(self, window, command)
			self.running = True
		else:
			self.tmux.execute(['new-window', '-dt', self.name, '-n', window.name, command])

	def _execute(self, window, cmd, *args):
		self.tmux.execute([cmd] + ['-t', '%s:%s' % (self.name, window.name)] + list(args))

	def attach(self):
		self.tmux.execute(['attach', '-t', self.name])
		return self

	def close(self):
		self.tmux.execute(['kill-session', '-t', self.name])
		return self


class Window(object):
	def __init__(self, session, name):
		self.session = session
		self.name = name
		self.running = False

	def run(self, program):
		if not self.running:
			self.session._startWindow(self, program)
			self.running = True
		return self


	def execute(self, cmd, *args):
		self.session._execute(self, cmd, *args)
		return self

	def sendKeys(self, keys):
		self.execute('send-keys', keys)
		return self

	def sendLine(self, keys):
		self.sendKeys(keys).sendKeys("Enter")
		return self

	def focus(self):
		self.execute('select-window')
		return self

	def close(self):
		self.execute('kill-window')
		return self


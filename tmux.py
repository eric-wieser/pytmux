import subprocess

class Tmux(object):
	def __init__(self, socket=None, use_256_colors=True):
		self.socket = socket
		self.use_256_colors = use_256_colors

	@property
	def base_command(self):
		command = ['tmux']
		if self.socket is not None:
			command += ['-S', self.socket]
		if self.use_256_colors:
			command += ['-2']

		return command

	def execute(self, cmd):
		subprocess.call(self.base_command + cmd)
		return self

	def _start_session(self, session, window, command):
		self.execute(['new-session', '-ds', session.name, '-n', window.name, command])

	def session(self, name):
		return Session(self, name)


class Session(object):
	def __init__(self, tmux, name):
		self.name = name
		self.tmux = tmux
		self.running = False

	def window(self, name):
		return Window(self, name)

	def _start_window(self, window, command):
		if not self.running:
			self.tmux._start_session(self, window, command)
			self.running = True
		else:
			self.tmux.execute(['new-window', '-a', '-dt', self.name, '-n', window.name, command])

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
			self.session._start_window(self, program)
			self.running = True
		return self

	def run_shell(self, cmds):
		return (self
			.run(program='')
			.send_keys(''.join(
				'{}\n'.format(cmd) for cmd in cmds
			))
		)

	def execute(self, cmd, *args):
		self.session._execute(self, cmd, *args)
		return self

	def send_keys(self, keys):
		return self.execute('send-keys', keys)

	def send_line(self, keys):
		return self.send_keys(keys).send_keys("Enter")

	def focus(self):
		return self.execute('select-window')

	def close(self):
		return self.execute('kill-window')


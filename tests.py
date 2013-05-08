from tmux import Tmux
from time import sleep
from threading import Thread

tmux = Tmux()
session = tmux.session('testing')

w2 = session.window('test').run('htop')
w1 = session.window('test2').run('zsh')

Thread(target = lambda: session.attach()).start()

sleep(1)
print "hi"

w2.focus()

sleep(1)

w1.focus()

sleep(2)

session.close()
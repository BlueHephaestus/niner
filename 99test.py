import keyboard as kb
from pynput.keyboard import Key, Controller
pykb = Controller()


import time
def on_triggered():
	s = "\b\bSomething completely different and not automated at alll uwu"
	pykb.type(s)

kb.add_word_listener("99a", on_triggered, triggers=["b"])

kb.wait()


import keyboard as kb


import time
def on_triggered():
	s = "\b\bSomething completely different and not automated at alll uwu"
	kb.write(s)

#s = "Something completely DIFFERENT and not automated at alll uw\n"
##time.sleep(0.5)
#kb.write(s)
time.sleep(0.5)
#kb.add_hotkey('space', lambda: print('space was pressed!'))
kb.press_and_release('shift+s, space')
time.sleep(0.5)
s = 'he Quick Brown Fox jumps over the lazy dog.'
kb.write('he ')
kb.press_and_release('shift+q')
kb.write('uick ')
kb.press_and_release('shift+b')
kb.write('rown fox jumps over the lazy dog.')
kb.press_and_release('shift+s, space')

#kb.add_word_listener("99a", on_triggered, triggers=["b"])
#kb.add_abbreviation('@@', 'my.long.email@example.com')
kb.wait()


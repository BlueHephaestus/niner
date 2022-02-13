import keyboard as listener
from pynput.keyboard import Key, Controller
import os, time, sys, subprocess
"""
Main file - handles all existing events, listening for them and adding new ones
	when created.

We use keyboard library for listening (since its unfortunately bugged on
	actual writing of keys)

And we use pynput for sending keys.

We have it configured so that there can be any length hotkeys, and assumed without
	any modifier keys. We handle the setup of add_word_listener to always work with it.
	Since the abbreviation method of the listener library both wouldn't handle
	the sending properly, as well as it wouldn't allow extending to actual
	arbitrary python code, which we may add later.
"""

sender = Controller()
metahotkey = "ctrl+9"
wrap_n = 100

def say(s):
	# Speak the given string, and hide stderr. Use what you have if it's simple (espeak).
	#subprocess.check_output(['espeak',f'"{s}"','-s','160','-a','30','-z'], stderr=subprocess.DEVNULL)
	subprocess.Popen(['espeak',f'"{s}"','-s','160','-a','30','-z'], stderr=subprocess.DEVNULL)

def slowtype(s):
	# Sometimes type breaks on clients with latency, so we add a tiny delay to fix this
	# Takes the same amount of time empirically by the way, I tested.
	for c in s:
		time.sleep(0.001)
		sender.tap(c)

#sender.type = slowtype

class Hotkey:
	def __init__(self, trigger, abbreviation=True, replacement=""):
		"""
		Initialize a hotkey. Doing so adds it to the ongoing listener object.

		trigger: The string to call this on.
		abbreviation: If this is a simple replace-string hotkey
			If this is true, replacement should be a string
		replacement: String to replace the input trigger string with, in the case of abbreviation=True
		"""
		self.trigger = trigger
		self.abbreviation = abbreviation
		self.replacement = replacement

		# Stuff to ensure we trigger when we want to with this library
		self._handler = listener.add_word_listener(trigger[:-1], self.optimized_callback, triggers=[trigger[-1]], match_suffix=False)

		#print(f"Loaded Hotkey '{self.trigger}' for '{self.replacement[:wrap_n]}...'")
		self.delay = 0

		# Characters that keyboard library can't handle, because it sucks,
		# and their resulting mapping which the shift key is applied to.
		self._shift_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()_+{}|:"<>?'
		self._shift_lower = "abcdefghijklmnopqrstuvwxyz`1234567890-=[]\;',./"
		self.shift_map = {upper:lower for upper,lower in zip(self._shift_upper, self._shift_lower)}

	def optimized_callback(self):
		t = time.time()
		if self.abbreviation:
			print(f"Triggered Hotkey '{self.trigger}' for '{self.replacement[:wrap_n]}...'")
			# Erase the input trigger string
			# For some reason pynput doesn't like '\b'
			for _ in range(len(self.trigger)):
				sender.tap(Key.backspace)

			# Iterate through letters, and try to minimize calls to .write
			# So we put all lowercase characters into chunks, 
			# separated when an upper case character comes along.
			# At the end if we still have a chunk to write, we write that.
			chunk = ""
			for letter in self.replacement:
				"""
				# Tried out limiting size, doesn't seem to make a diff
				if len(chunk) > 10:
					listener.write(chunk)
					chunk = ""
				"""
				if letter not in self.shift_map:
					chunk += letter
				else:
					# letter is in our map
					if self.delay != 0:
						time.sleep(self.delay)
					listener.write(chunk)
					listener.press_and_release('shift+' + self.shift_map[letter])
					chunk = ""

			if chunk != "":
				listener.write(chunk)
		else:
			# Used to enable/disable typing delay
			if self.delay == 0:
				say("Slow Mode Enabled")
				self.delay = 0.1
			else:
				say("Slow Mode Disabled")
				self.delay = 0
		print(time.time()-t)


	def callback(self):
		t = time.time()
		if self.abbreviation:
			print(f"Triggered Hotkey '{self.trigger}' for '{self.replacement[:wrap_n]}...'")
			# Erase the input trigger string
			# For some reason pynput doesn't like '\b'
			for _ in range(len(self.trigger)):
				sender.tap(Key.backspace)
			sender.type(self.replacement) # Type what this was an abbreviation for
		print(time.time()-t)
	
	def remove(self):
		# Lib doesn't handle this properly for when there are multiple with the
		# same prefix, so I actually modified the library.
		# keyboard/__init__.py, line 1118, added checks before each of the del lines so we don't get errors.
		listener.remove_word_listener(self._handler)

def events_to_trigger(events):
	# Convert list of KeyboardEvents to a trigger string
	# These come in from a recording object,
	# and so we have to remove the events that triggered the recording and also ended it.
	trigger = ""

	# Since this is triggered by ctrl + 9, the first two events will be us releasing those two keys.
	# the last n events will be us pressing those keys.
	# So we want to ignore everything but the events within those keys.
	# For the events within those keys, we only pay attention to the down keys.
	# We do this by looking only from the 3rd event onward, and doing so until we reach a ctrl+9 down pair.
	# Note this won't occur on 9 + ctrl, since that's a different keybind.
	# We also unfortunately can have events where we press ctrl down for a long time before pressing 9,
	# so we have to remove all duplicates in that case.
	all_ctrl_down = lambda events: all([(event.name=="ctrl" and event.event_type=="down") for event in events])

	# We could shorten this by removing all upstrokes but this would make it impossible to end
	# with a ctrl keybind, and I'd rather leave that for max generalization
	
	# Remove the starter keybinds
	events = events[2:]
	for i,event in enumerate(events[:-1]):
		# check if we're at our termination string (ctrl+9, both down)
		# Via checking if this event and all events up until the last one are ctrl + down.
		if all_ctrl_down(events[i:-1]):
			# they were all ctrl, check if the last one is 9 down
			if events[-1].name == "9" and events[-1].event_type=="down":
				break
		
		# Otherwise add this if it's a downstring.
		elif event.event_type == "down":
			#print(event.name)
			trigger += event.name

	return trigger

def add_new_hotkey():
	# On pressing ctrl+9, will use the current clipboard as the replacement for whatever
	# abbreviation is typed in next.
	# For example, let's say I select the text "By the way, ", and copy it.
	# I then press 'ctrl+9', because i use this phrase a lot and would like to shortcut it.
	# This function will then be triggered, and I type in "9btw", to make sure i don't
	# ever accidentally type it in.
	# This will now save that forever, unless i delete the "9btw.txt" file in the hotkeys folder.
	# Any future types of "9btw" will automatically insert that.
	say("Listening")
	print("Current clipboard grabbed. Type your abbreviation/hotkey now...")
	replacement = os.popen('xsel').read()

	# Record all inputs until ctrl+9 is pressed again
	events = listener.record(until=metahotkey)

	# Parse the actual trigger string from the events list
	trigger = events_to_trigger(events)
	if len(trigger) > 1:
		print(f"You selected '{trigger}' as your hotkey")

		# Add as new hotkey via writing it to the file.
		# This will replace any others if they exist there.
		with open(hotkey_dir + trigger + ".txt", "w") as f:
			f.write(replacement)

		print(f"Saved Hotkey '{trigger}' for '{replacement[:wrap_n]}'...")
		say("Saved")
	else:
		print("Ignoring Hotkey and Refreshing...")
		say("Ignoring")
		
	

if __name__ == "__main__":
	while True:
		# Main daemon loop - use Ctrl+C on the main program to kill it
		# Re loads listeners on every iteration to ensure we never have any 
		# duplicated or overlapping hotkeys.
		#
		# Load existing hotkeys
		hotkeys = {} # For tracking purposes
		hotkey_dir = "hotkeys/"
		for hotkey_fname in os.listdir("hotkeys/"):
			trigger, ext = os.path.splitext(hotkey_fname)
			if ext == ".txt":
				# is an abbreviation, meaning the filename is the abbreviation trigger.
				# e.g. btw.txt -> "By the way, "
				replacement = open(hotkey_dir + hotkey_fname).read().strip()
				hotkeys[trigger] = Hotkey(trigger, abbreviation=True, replacement=replacement)

		# Temp, trying to add one for slow mode toggle.
		hotkeys["sm9"] = Hotkey("sm9", abbreviation=False, replacement=None)

		# Start listening for our metahotkey - to add new hotkeys.
		# This is not included in the files to avoid conflicts. Do not overwrite it.
		print("Listening for Hotkeys...")
		#listener.add_word_listener("999", add_new_hotkey, triggers=["9"], match_suffix=True)
		#listener.add_hotkey("ctrl+9", add_new_hotkey)

		# Limitation of listener library is it can't have another .wait() command running at the same time
		# so in order to dynamically add hotkeys while running, we have to interrupt program execution
		# via our metahotkey, then add the hotkey, then reload the loop.
		listener.wait(metahotkey)

		# Remove any hotkeys so we can overwrite if the new hotkey needs to.
		for trigger,hotkey in hotkeys.items():
			hotkey.remove()

		add_new_hotkey()

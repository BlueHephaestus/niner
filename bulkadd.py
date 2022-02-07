"""
Make use of input to bulk add a bunch of new shortcuts repeatedly.
	Also helpful to make sure you get them right.
"""

hotkeys_dir = "hotkeys/"
while True:
	trigger = input("Trigger: ")
	replacement = input("Replacement: ")
	shortcut_str = f"'{trigger}' -> '{replacement[:100]}'"
	confirm = input(f"Confirm? {shortcut_str} (Y/n)")
	if "n" in confirm.lower():
		print("Cancelled; Shortcut not added.")

	else:
		# Add it
		try:
			with open(hotkeys_dir + trigger + ".txt", "w") as f:
				f.write(replacement)

			print(f"Added {shortcut_str}")

		except:
			print("Error encountered trying to add shortcut. Make sure your trigger is a valid filename.")

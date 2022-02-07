# Small UI to always show most updated shortcuts.
import sys, os, time
from subprocess import call

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

hotkeys_dir = "hotkeys/"
refresh_rate = 1
wrap_n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
call('clear')
while True:
	fnames = sorted([fname for fname in os.listdir(hotkeys_dir)])
	for fname in fnames:
		trigger, ext = os.path.splitext(fname)
		if ext == ".txt":
			replacement = open(hotkeys_dir + fname).read().strip()
			print(f"{bcolors.OKGREEN}{trigger.ljust(10)} -> {bcolors.OKBLUE}{replacement[:wrap_n]}{bcolors.ENDC}")

	time.sleep(refresh_rate)
	call('clear')

		


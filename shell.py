"""
Extension to just bulkadd, this will actually functiona as a shell interface to niner and its hotkeys.
    Since i'm finding that easier for editing than having dynamic ones + tts.
"""

import cmd, sys
import os.path
import shutil
from utils.loop_utils import persistent

trigger_dir = "triggers/"
blob_prefix = "blob-"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def printgreen(s):
    print(f"{bcolors.OKGREEN}{s}{bcolors.ENDC}")

def printred(s):
    print(f"{bcolors.FAIL}{s}{bcolors.ENDC}")


#TODO add blobmv, blobrm commands?
class NinerShell(cmd.Cmd):
    intro = 'Welcome to the Niner shell.   Type help or ? to list commands.\n'
    prompt = '(niner) '
    file = None

    # need one that's a loner, and one that works regardless
    # we have those that always trigger, and those that only trigger
    # By default we add as abbreviation, if they pass -a or --always it always triggers
    def do_abbr(self, args):
        'Add a new trigger, payload pair as an abbreviation (trigger must be alone): abbr <trigger> <payload>, e.g. abbr ty thank you'
        # if one exists then it will be replaced with this
        #try:
        trigger, payload = parse(args)
        with open(trigger_dir + trigger + ".txt", "w") as f:
            f.write(payload)
        # Add capitalized counterpart if not already there
        # Note: doesn't include this case in the other cases. Just helps add more.
        if trigger[0] != "0":
            self.do_abbr("0" + trigger + " " + payload.capitalize())

        printgreen(f"Added Abbreviation {trigger} -> {payload}")

        #except:
        #printred("Error encountered trying to add abbreviation. Make sure your trigger is a valid filename.")

    def do_blob(self, args):
        'Add a new trigger, payload pair as a blob (trigger can be anywhere): blob <trigger> <payload>, e.g. blob np no problem'
        # if one exists then it will be replaced with this
        try:
            trigger, payload = parse(args)
            with open(trigger_dir + blob_prefix + trigger + ".txt", "w") as f:
                f.write(payload)

            printgreen(f"Added Blob {trigger} -> {payload}")

        except:
            printred("Error encountered trying to add blob. Make sure your trigger is a valid filename.")

    def do_rm(self, args):
        'Remove a trigger, payload pair by referencing the trigger: rm <trigger>, e.g. rm ty'
        trigger = parse(args)[0]
        trigger_file = trigger_dir + trigger + ".txt"
        blob_trigger_file = trigger_dir + blob_prefix + trigger + ".txt"

        # Check for if it's a blob or abbr, will remove only one.
        if os.path.isfile(trigger_file):
            os.remove(trigger_file)
            printgreen(f"Removed {trigger}")
        elif os.path.isfile(blob_trigger_file):
            os.remove(blob_trigger_file)
            printgreen(f"Removed {blob_prefix + trigger}")
        else:
            printred(f"Trigger File does not exist.")
        try:
            pass

        except:
            printred("Error encountered trying to remove trigger. Make sure your trigger exists or is spelled correctly.")

    def do_mv(self, args):
        'Move/Rename a trigger: mv <trigger1> <trigger2>, e.g. mv ty thx'
        # Also this is explicit, if you want to move a blob make sure to specify blob-trigger not just trigger
        try:
            trigger_src, trigger_dst = parse(args)
            trigger_src_file = trigger_dir + trigger_src + ".txt"
            trigger_dst_file = trigger_dir + trigger_dst + ".txt"

            # Will delete dst file if it exists
            if os.path.isfile(trigger_src_file):
                os.replace(trigger_src_file, trigger_dst_file)
                printgreen(f"Moved {trigger_src} -> {trigger_dst}")
            else:
                printred(f"Trigger File does not exist.")

        except:
            printred("Error encountered trying to move trigger. Make sure your trigger exists or is spelled correctly.")

    def do_cp(self, args):
        'Copy a trigger: cp <trigger1> <trigger2>, e.g. cp ty thx'
        # Also this is explicit, if you want to move a blob make sure to specify blob-trigger not just trigger
        try:
            trigger_src, trigger_dst = parse(args)
            trigger_src_file = trigger_dir + trigger_src + ".txt"
            trigger_dst_file = trigger_dir + trigger_dst + ".txt"

            # Will overwrite / delete dst file if it exists
            if os.path.isfile(trigger_src_file):
                # gotta use shutil here apparently otherwise we have to create all sorts of stuff.
                shutil.copy(trigger_src_file, trigger_dst_file)
                printgreen(f"Copied {trigger_src} -> {trigger_dst}")
            else:
                printred(f"Source Trigger File does not exist.")

        except:
            printred("Error encountered trying to copy trigger. Make sure your trigger exists or is spelled correctly.")

    def do_edit(self, args):
        'Edit payload of a trigger: edit <trigger> <new payload>, e.g. edit ty thank you very much'
        # Convenience method, since abbr and blob require knowing if it's an abbr or blob. This will figure it out
        # and replace the payload with the given new text.
        try:
            trigger, payload = parse(args)
            trigger_file = trigger_dir + trigger + ".txt"
            blob_trigger_file = trigger_dir + blob_prefix + trigger + ".txt"

            # Check for if it's a blob or abbr, will edit only one.
            # HIGHLY RECOMMEND NOT HAVING BLOBS AND ABBRS WITH SAME TRIGGER
            if os.path.isfile(trigger_file):
                with open(trigger_file, "w") as f:
                    f.write(payload)
                printgreen(f"Updated {trigger} -> {payload}")
            elif os.path.isfile(blob_trigger_file):
                with open(blob_trigger_file, "w") as f:
                    f.write(payload)
                printgreen(f"Updated {blob_prefix + trigger} -> {payload}")
            else:
                printred(f"Trigger File does not exist.")

        except:
            printred("Error encountered trying to edit trigger payload. Make sure your trigger exists or is spelled correctly.")


    #TODO update to take args so we can specify what to filter for?
    def do_ls(self, args):
        'List all triggers and payloads: ls <optional trigger or trigger substring>, e.g. ls ty'

        try:
            if len(args) > 0:
                query = parse(args)[0]
            else:
                query = ""
            fnames = sorted([fname for fname in os.listdir(trigger_dir)])
            for fname in fnames:
                trigger, ext = os.path.splitext(fname)
                #if ext == ".txt" and trigger.startswith(query):
                if ext == ".txt" and query in trigger:
                    payload = open(trigger_dir + fname).read().strip()
                    print(f"{bcolors.OKGREEN}{trigger.ljust(10)} -> {bcolors.OKBLUE}{payload}{bcolors.ENDC}")
        except:
            printred("Error encountered trying to edit trigger payload. Make sure your trigger exists or is spelled correctly.")

    def do_lst(self, _):
        'List all triggers: lst'
        fnames = sorted([fname for fname in os.listdir(trigger_dir)])
        line = ""
        for fname in fnames:
            trigger, ext = os.path.splitext(fname)
            if ext == ".txt":
                if len(line) < 100:
                    line += trigger.ljust(10) + " "
                else:
                    printgreen(line)
                    line = trigger.ljust(10) + " "
        if len(line) != 0:
            printgreen(line)


def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    'Convert a series of strings to an argument tuple (trigger, payload)'
    return tuple(arg.split(maxsplit=1))

@persistent
def main():
	NinerShell().cmdloop()

if __name__ == '__main__':
	main()

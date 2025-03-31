#! /usr/bin/python

###############################################################################
# 
# Julian Parkin 2025-03-31
# 
# Script to use the BMC Disco built-in tw_scan_control to manage scans.
# Initial implementation is designed to Disable all scheduled scans and keep
# a record of which ones were Enabled before taking action, which will then
# allow us to Enable only those that were Enabled before we took action.
#
# Consider taking a copy of 'tw_scan_control --list' before using this.
#
###############################################################################

import argparse, sys
from subprocess import STDOUT, PIPE, Popen
from getpass import getpass

parser = argparse.ArgumentParser(
    description="Uses BMC Discovery built-in tw_scan_control to bulk-manage scheduled scans.",
    epilog="Julian Parkin 2025-03-31",
    usage="%(prog)s [options]")
parser.add_argument("-v", "--verbose",
                    help="increase output verbosity",
                    action="store_true")
parser.add_argument("--schedule_list",
                    help="list all scheduled scans",
                    action="store_true")
parser.add_argument("--schedule_list_enabled",
                    help="list all enabled scheduled scans",
                    action="store_true")
parser.add_argument("--schedule_pause",
                    help="disable all enabled scheduled scans",
                    action="store_true")
parser.add_argument("--schedule_resume",
                    help="re-enable scheduled scans that were disabled last time --schedule_pause was run",
                    action="store_true")
args = parser.parse_args()

# TODO check for an existing list of jobs and prompt the user before removing

# user needs to provide disco system password
guipw = getpass("Password for BMC Discovery UI user system:")

if(args.schedule_list):
    cmd = str.encode("tw_scan_control --password " + guipw + " --list")
    with Popen([cmd], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
        out, err = proc.communicate()
        if err: print(err.decode('utf-8')); sys.exit("Aborting")
        print(out.decode('utf-8'))

if(args.schedule_list_enabled):
    cmd = str.encode("tw_scan_control --password " + guipw + " --list | egrep '^[a-zA-Z0-9]+\sTrue\s'")
    with Popen([cmd], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
        out, err = proc.communicate()
        if err: print(err.decode('utf-8')); sys.exit("Aborting")
        print(out.decode('utf-8'))

if(args.schedule_pause):
    # gather the existing list of scheduled jobs where Enabled=True
    cmd = str.encode("tw_scan_control --password " + guipw + " --list | egrep '^[a-zA-Z0-9]+\sTrue\s' > schedule_enabled_list.txt")
    with Popen([cmd], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
        out, err = proc.communicate()
        if err: print(err.decode('utf-8')); sys.exit("Aborting")
        if args.verbose: print(out.decode('utf-8'))
    # put file contents into a list of scheduled jobs
    with open("schedule_enabled_list.txt", 'r') as f:
        schedule = f.read().splitlines()
        if args.verbose: print(*schedule, sep ='\n')
    # use tw_scan_control to disable each scan
    for scan in schedule:
        cmd = str.encode("tw_scan_control --password " + guipw + " --disable " + scan.split(" ", 1)[0])
        if args.verbose: print("tw_scan_control --disable " + scan.split(" ", 1)[0])
        with Popen([cmd], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
            out, err = proc.communicate()
            if err: print(err.decode('utf-8')); sys.exit("Aborting")
            if args.verbose: print(out.decode('utf-8'))

if(args.schedule_resume):
    # gather the existing list of scheduled jobs captured by schedule_pause
    with open("schedule_enabled_list.txt", 'r') as f:
        schedule = f.read().splitlines()
        if args.verbose: print(*schedule, sep ='\n')
    # use tw_scan_control to enable each scan
    for scan in schedule:
        cmd = str.encode("tw_scan_control --password " + guipw + " --enable " + scan.split(" ", 1)[0])
        if args.verbose: print("tw_scan_control --enable " + scan.split(" ", 1)[0])
        with Popen([cmd], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
            out, err = proc.communicate()
            if err: print(err.decode('utf-8')); sys.exit("Aborting")
            if args.verbose: print(out.decode('utf-8'))
    # looks successful; delete or archive the schedule file?

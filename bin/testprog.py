#!/usr/bin/python
import os
import re
import sys
import time
import shutil
import filecmp
from subprocess import Popen, PIPE
from os import path

CCTF_PATH = os.getenv("CCTF_PATH", "/var/cctf")
SRC_NAME = os.getenv("SRC_NAME", "")
BIN_NAME = os.getenv("BIN_NAME", SRC_NAME)
if not BIN_NAME:
    BIN_NAME = SRC_NAME
TEAMS = int(os.getenv("TEAMS", "1"))
if not BIN_NAME:
    print "BIN_NAME not set. It must be!"
    sys.exit(1)
PATH1 = CCTF_PATH + "/dirs/"
PATH2 = "/bin/" + BIN_NAME
GOLD = CCTF_PATH + "/bin/gold"
TIMEOUT = 1
LOOP_TIME = 0.002
# TODO(derpferd): Maybe put these into config file.
CHECK_FILES = True
CHECK_ERR = True
CHECK_OUT = True
CHECK_EXIT_CODE = False


def are_dirs_same(a, b, ignore=[]):
    r = filecmp.dircmp(a, b, ignore)
    return r.right_only == r.left_only == r.diff_files == []


def get_diff_string(a, b, ignore=[]):
    r = filecmp.dircmp(a, b, ignore)
    s = ""
    if r.right_only != []:
        s += "only right has: " + str(r.right_only) + "   "
    if r.left_only != []:
        s += "only left has: " + str(r.left_only) + "   "
    if r.diff_files != []:
        s += "no matchy:" + str(r.diff_files)
    return s


def attack_to_args(attack):
    # This is an attempt to parse the argument string using regex.
    #matches = re.findall(r'(["\'][-\w\s]*["\']|([\w-]*(\\ )*[\w-]*)*)', attack)
    # Remove all blanks
    #args = map(lambda x: x[0], filter(lambda x: x[0], matches))
    #return args

    # TODO(derpferd): make single quotes and backslashes work.
    args = attack.split()  # Split on the spaces

    # put quotes that were split back together
    i = 0
    in_quote = False
    while i < len(args):
        if in_quote:
            args[i-1] += " " + args.pop(i)
            i -= 1
        if args[i].count('"') % 2 == 1:
            in_quote = True
        else:
            in_quote = False
        i += 1

    for i in range(len(args)):
        args[i] = args[i].replace('"', "")

    return args


def test_attack(team, args):
    print "Calling Attack..."
    if team in [str(i+1) for i in range(TEAMS)]:
        team = "team" + team
    if team not in ["team"+str(i+1) for i in range(TEAMS)]:
        raise Exception("Invalid team.")

    print team.title() + ",", args

    prog = PATH1 + team + PATH2
    print "prog", prog
    if not path.exists(prog):
        print "Could not find user's program!"
        return False
    if not path.exists(GOLD):
        raise Exception("Could not find the gold program!")
        return True

    def clean_up():
        if os.path.exists(CCTF_PATH+"/cur_env"):
            shutil.rmtree(CCTF_PATH+"/cur_env")
        if os.path.exists(CCTF_PATH+"/gold_env"):
            shutil.rmtree(CCTF_PATH+"/gold_env")

    clean_up()
    shutil.copytree(CCTF_PATH+"/env", CCTF_PATH+"/cur_env")
    shutil.copytree(CCTF_PATH+"/env", CCTF_PATH+"/gold_env")

    calc_process = Popen([prog] + args, stdout=PIPE, stderr=PIPE, cwd=CCTF_PATH + "/cur_env")

    start_time = time.time()
    calc_exit_code = calc_process.poll()
    while calc_exit_code is None:
        time.sleep(LOOP_TIME)
        calc_exit_code = calc_process.poll()
        if time.time() - start_time > TIMEOUT:
            calc_process.kill()
            clean_up()
            print "User's program was killed."
            return False

    calc_out, calc_err = calc_process.communicate()

    gold_process = Popen([GOLD] + args, stdout=PIPE, stderr=PIPE, cwd=CCTF_PATH + "/gold_env")
    gold_exit_code = gold_process.poll()
    while gold_exit_code is None:
        time.sleep(LOOP_TIME)
        gold_exit_code = gold_process.poll()
        if time.time() - start_time > TIMEOUT:
            gold_process.kill()
            print "This is a very bad bug!!!! Please let your Instructor know about this: Gold has a bug!"
            clean_up()
            return False

    gold_out, gold_err = gold_process.communicate()

    print "!!WARNING!!!! stderr has been regexed!"
    gold_err = re.sub(r'^[/\.\w]*/prog:', r'', gold_err)
    calc_err = re.sub(r'^[/\.\w]*/'+BIN_NAME+r':', r'', calc_err)

    print "Out: '" + str(calc_out) + "'"
    print "Gold out: '" + str(gold_out) + "'"
    print "Err: '" + str(calc_err) + "'"
    print "Gold Err: '" + str(gold_err) + "'"
    print "Exit Code: '" + str(calc_exit_code) + "'"
    print "Gold Exit Code: '" + str(gold_exit_code) + "'"
    diff_string = get_diff_string(CCTF_PATH+"/cur_env", CCTF_PATH+"/gold_env", ["prog", BIN_NAME])
    if diff_string:
        print "File status:", diff_string
    else:
        print "Files do not differ!"

    if not CHECK_OUT:
        print "!!!WARNING!!! Not comparing stdout in check, FYI"
    if not CHECK_ERR:
        print "!!!WARNING!!! Not comparing stderr in check, FYI"
    if not CHECK_FILES:
        print "!!!WARNING!!! Not comparing files in check, FYI"
    if not CHECK_EXIT_CODE:
        print "!!!WARNING!!! Not comparing exit code in check, FYI"

    checks = set()
    if CHECK_OUT:
        checks.add(calc_out == gold_out)
    if CHECK_ERR:
        checks.add(calc_err == gold_err)
    if CHECK_FILES:
        checks.add(are_dirs_same(CCTF_PATH+"/cur_env", CCTF_PATH + "/gold_env", ["prog", BIN_NAME]))
    if CHECK_EXIT_CODE:
        checks.add(calc_exit_code == gold_exit_code)

    if checks == {True}:
        clean_up()
        print "-- All is well"
        print "Cleaned up and ready for the next one!\n\n"
        return True
    else:
        if CHECK_OUT and calc_out != gold_out:
            print "-- Out does not match"
        if CHECK_ERR and calc_err != gold_err:
            print "-- Err does not match"
        if CHECK_FILES and not are_dirs_same(CCTF_PATH+"/cur_env", CCTF_PATH+"/gold_env", ["prog", BIN_NAME]) != gold_out:
            print "-- Directories do not match"
        if CHECK_EXIT_CODE and calc_exit_code != gold_exit_code:
            print "-- Exit codes do not match"
        clean_up()
        print "-- User's program didn't pass"
        print "Cleaned up and ready for the next one!\n\n"
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print """Need more args."""
    if test_attack(sys.argv[1], sys.argv[2:]):
        print "Passed."
    else:
        print "Failed."

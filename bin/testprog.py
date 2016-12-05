#!/usr/bin/python
import os
import sys
import time
import shutil
import filecmp
from subprocess import Popen, PIPE
from os import path

CCTF_PATH = os.getenv("CCTF_PATH", "/var/cctf")
SRC_NAME = os.getenv("SRC_NAME", "")
BIN_NAME = os.getenv("BIN_NAME", SRC_NAME)
if not BIN_NAME: BIN_NAME = SRC_NAME
TEAMS = int(os.getenv("TEAMS", "1"))
if not BIN_NAME:
  print "BIN_NAME not set. It must be!"
  sys.exit(1)
PATH1 = CCTF_PATH + "/dirs/"
PATH2 = "/bin/" + BIN_NAME
GOLD = CCTF_PATH+ "/bin/gold"
TIMEOUT = 1
LOOP_TIME = 0.002
CHECK_FILES = True


def are_dirs_same(a, b, ignore=[]):
    r = filecmp.dircmp(a, b, ignore)
    return r.right_only == r.left_only == r.diff_files == []

def attack_to_args(attack):
  args = attack.split()

  # put quotes togather
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
    args[i] = args[i].replace('"',"")

  return args

#print attack_to_args('"1 + 2"')  


def test_attack(team, args):
  if team in [str(i+1) for i in range(TEAMS)]:
    team = "team" + team
  if team not in ["team"+str(i+1) for i in range(TEAMS)]:
    raise Exception("Invalid team.")

#  print team, args

  prog = PATH1 + team + PATH2
  if not path.exists(prog):
    return False
  if not path.exists(GOLD):
    return True

  #os.chdir(CCTF_PATH+"/cur_env")
  def clean_up():
    #os.chdir(CCTF_PATH)
    if os.path.exists(CCTF_PATH+"/cur_env"):
      shutil.rmtree(CCTF_PATH+"/cur_env")
    if os.path.exists(CCTF_PATH+"/gold_env"):
      shutil.rmtree(CCTF_PATH+"/gold_env")
  
  clean_up()
  shutil.copytree(CCTF_PATH+"/env", CCTF_PATH+"/cur_env")
  shutil.copytree(CCTF_PATH+"/env", CCTF_PATH+"/gold_env")
#  print "PROG:", prog

  calc_process = Popen([prog] + args, stdout=PIPE, cwd=CCTF_PATH+"/cur_env")

  start_time = time.time()
  calc_exit_code = calc_process.poll()
  while calc_exit_code is None:
    time.sleep(LOOP_TIME)
    calc_exit_code = calc_process.poll()
    if time.time() - start_time > TIMEOUT:
      calc_process.kill()
      clean_up()
      return False

  (calc_output, err) = calc_process.communicate()


  
#  print >> sys.stderr, "Starting Gold..."
  gold_process = Popen([GOLD] + args, stdout=PIPE, cwd=CCTF_PATH+"/gold_env")
#  print >> sys.stderr, "Polling..."
  gold_exit_code = gold_process.poll()
  while gold_exit_code is None:
    time.sleep(LOOP_TIME)
    gold_exit_code = gold_process.poll()
#    print "Waiting for gold."
    if time.time() - start_time > TIMEOUT:
      gold_process.kill()
      print "This is a very bad bug!!!! Please let your Instructor know about this: Gold has a bug!"
      clean_up()
      return False

  (gold_output, err) = gold_process.communicate()

#  print "Output: '" + str(calc_output) + "'"
#  print "Output Gold: '" + str(gold_output) + "'"
#  print "Exit Code:", exit_code

  if calc_exit_code == gold_exit_code and calc_output == gold_output and are_dirs_same(CCTF_PATH+"/cur_env", CCTF_PATH+"/gold_env", ["gold", prog]):
    clean_up()
    return True
  else:
    clean_up()
    return False


#print attack_to_args("\"213443\" sdfj \"sdakflj ief 8\" 9dsf \"34\" dfshjk")
#test_attack("team1", [])

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print """Need more args."""
    #raise Exception("Need more args.\nUsage: testprog team args")
  if test_attack(sys.argv[1], sys.argv[2:]):
    print "Passed."
  else:
    print "Failed."

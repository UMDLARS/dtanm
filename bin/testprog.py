#!/usr/bin/python
import sys
import time
from subprocess import Popen, PIPE
from os import path


PATH1 = "/var/cctf/dirs/"
PATH2 = "/bin/calc"
GOLD = "/var/cctf/bin/gold"
TIMEOUT = 1
LOOP_TIME = 0.002


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
  if team in ["1", "2", "3", "4"]:
    team = "team" + team
  if team not in ["team1", "team2", "team3", "team4"]:
    raise Exception("Invalid team.")

#  print team, args

  prog = PATH1 + team + PATH2
  if not path.exists(prog):
    return False
  if not path.exists(GOLD):
    return True

#  print "PROG:", prog

  calc_process = Popen([prog] + args, stdout=PIPE)

  start_time = time.time()
  calc_exit_code = calc_process.poll()
  while calc_exit_code is None:
    time.sleep(LOOP_TIME)
    calc_exit_code = calc_process.poll()
    if time.time() - start_time > TIMEOUT:
      calc_process.kill()
      return False

  (calc_output, err) = calc_process.communicate()


#  print >> sys.stderr, "Starting Gold..."
  gold_process = Popen([GOLD] + args, stdout=PIPE)
#  print >> sys.stderr, "Polling..."
  gold_exit_code = gold_process.poll()
  while gold_exit_code is None:
    time.sleep(LOOP_TIME)
    gold_exit_code = gold_process.poll()
#    print "Waiting for gold."
    if time.time() - start_time > TIMEOUT:
      gold_process.kill()
      print "This is a very bad bug!!!! Please let Jonathan Beaulieu know about this."
      return False

  (gold_output, err) = gold_process.communicate()


#  print "Output: '" + str(calc_output) + "'"
#  print "Output Gold: '" + str(gold_output) + "'"
#  print "Exit Code:", exit_code

  if calc_exit_code == gold_exit_code and calc_output == gold_output:
    return True
  else:
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

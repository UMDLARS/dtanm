import os
import sys
import time

HOME_PATH = os.getenv("HOME_PATH", "/home")
CCTF_PATH = os.getenv("CCTF_PATH", "/var/cctf")
TEAMS = int(os.getenv("TEAMS", "1"))


def list_dir_non_hidden(path):
  files = os.listdir(path)
  return filter(lambda x: x[0] != ".", files)


def get_lowest(path):
  files = list_dir_non_hidden(path)
  return min(map(lambda x: path + x, files), key=os.path.getctime)

print "Starting..."
c = 0
attacks = 0
while 1:
  c += 1
  sys.stdout.write("\033[F")
  print "Looking." + ("." * (c %3)) + "  \tAttacks grabbed:", attacks
  new_lines = set()
  for i in range(TEAMS):
    team_path = HOME_PATH + "/team" + str(i+1) + "/attacks/"
    if list_dir_non_hidden(team_path):
      lowest = get_lowest(team_path)
      if lowest:
        first_line = open(lowest, "r").readline()
        if first_line[-1] != "\n":
          first_line += "\n"
        new_lines.add(first_line)
        os.remove(lowest)
        attacks += 1
  
  old_lines = set(open(CCTF_PATH + "/attacklist.txt", "r").readlines())
  diff = new_lines.difference(old_lines)
  fp = open(CCTF_PATH + "/attacklist.txt", "a")
  fp.write("".join(diff))
  fp.close()
  time.sleep(1)

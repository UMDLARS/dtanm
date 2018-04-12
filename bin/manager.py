#!/usr/bin/python
from __future__ import print_function
import os
import sys
import time

HOME_PATH = os.getenv("HOME_PATH", "/cctf/server/uploads")
CCTF_PATH = os.getenv("CCTF_PATH", "/cctf")
TEAMS = int(os.getenv("TEAMS", "1"))


def list_dir_non_hidden(path):
  files = os.listdir(path)
  return filter(lambda x: x[0] != ".", files)


def get_lowest(path):
  files = list_dir_non_hidden(path)
  return min(map(lambda x: path + x, files), key=os.path.getctime)


def get_attack_from_file(fp):
  first_line = fp.readline()
  if len(first_line) == 0 or first_line[-1] != "\n":
    first_line += "\n"
  return first_line

def update_team_dirs(folders):
    for folder in folders:
        if not os.path.exists(CCTF_PATH + '/dirs/' +  folder):
            os.makedirs(CCTF_PATH + '/dirs/' + folder); 

def main():
  print("Starting...")
  c = 0
  attacks = 0
  while 1:
    c += 1
    sys.stdout.write("\033[F")
    print("Looking." + ("." * (c % 3)) + "  \tAttacks grabbed:", attacks)
    new_lines = set()
    # for i in range(TEAMS):
    for folder in os.listdir(HOME_PATH):
      team_path = HOME_PATH + '/'+ folder + "/attacks/"
      if list_dir_non_hidden(team_path):
        lowest = get_lowest(team_path)
        if lowest:
          with open(lowest, "r") as fp:
            attack = get_attack_from_file(fp)
            new_lines.add(attack)
            os.remove(lowest)
            attacks += 1
    
    old_lines = set(open(CCTF_PATH + "/attacklist.txt", "r").readlines())
    diff = new_lines.difference(old_lines)
    fp = open(CCTF_PATH + "/attacklist.txt", "a")
    fp.write("".join(diff))
    fp.close()
    time.sleep(1)

if __name__ == "__main__":
  main()

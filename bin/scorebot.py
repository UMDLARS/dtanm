import time
import testprog
import json

RELOAD_TIME = 30

def score():
  data = {}
  attack_fp = open("/var/cctf/attacklist.txt", "r")
  #math_fp = open("/var/cctf/goodmath.txt", "r")
  teams = ["team1", "team2", "team3", "team4"]
  team_fps = {}
  attack_count = 0
  totals = {}
  for team in teams:
    team_fps[team] = open("/var/cctf/dirs/" + team + "/score.txt", 'w')
    totals[team] = 0

  lines = attack_fp.readlines()
  #lines += math_fp.readlines()[:len(lines)]

  for attack in lines:
    attack_count += 1
    for team in teams:
      if attack and attack[-1] == "\n":
        attack = attack[:-1]
      print "Testing:", attack
      result = testprog.test_attack(team, testprog.attack_to_args(attack))
      result_str = "Failed"
      if result:
        result_str = "Passed"
        totals[team] += 1
      team_fps[team].write(result_str + " - '" + attack + "'\n")

  scoreboard_fp = open("/var/cctf/scoreboard.txt", 'w')
  for team in teams:
    scoreboard_fp.write(team+" "+str(totals[team])+"/"+str(attack_count)+"\n")

  data["teams"] = teams
  data["scores"] = totals
  data["total"] = attack_count
  json.dump(data, open("/var/cctf/scoreboard.json", 'w'))

if __name__ == "__main__":
  while True:
    start_time = time.time()
    score()
    end_time = time.time()
    print "Reloaded Scoreboard @", time.ctime()
    elapsed_time = end_time - start_time
    if elapsed_time < RELOAD_TIME:
      time.sleep(RELOAD_TIME - elapsed_time)
#!/usr/bin/python
from __future__ import print_function

import os
import pwd
import sys
import time
import testprog
import json
from multiprocessing import Process, Queue


class Scorer(Process):
    SUBMIT_URL = "http://127.0.0.1:8000/result"
    def __init__(self, queue):
        self.queue = queue
        super().__init__()

    def run(self):
        try:
            while 1:
                task = self.queue.get()
                if task is None:
                    break
                self.score(task)
        except KeyboardInterrupt:
            # TODO: clean up running child processes.
            pass

        print("Scorer Process dying...")

#    def __init__(self, hp, cp, rt):
#        self.RELOAD_TIME = rt  # Seconds
#        self.HOME_PATH = hp
#        self.CCTF_PATH = cp
    def score(self, task):
        print("Scoring: {}".format(task))
        # Create tmp directory.
        # Copy in env files.
        # Copy team's source code in and get the git commit hash.
        # Change the owner of the tmp_dir to the scorer user.
        # Get their program's output
        # Compare with gold's.
        # make request to results server with results from test.
        pass

    def score_old(self):
        data = {}
        attack_fp = open(self.CCTF_PATH+"/attacklist.txt", "r")
        good_fp = None
        if os.path.exists(self.CCTF_PATH+"/good.txt"):
            good_fp = open(self.CCTF_PATH+"/good.txt", "r")
        # teams = ["team"+str(i+1) for i in range(TEAMS)]
        teams = os.listdir(self.HOME_PATH)
        team_fps = {}
        attack_count = 0
        totals = {}
        for team in teams:
            team_fps[team] = open(self.CCTF_PATH+"/dirs/" + team + "/score.txt", 'w')
            totals[team] = 0

        lines = attack_fp.readlines()
        if good_fp:
            lines += good_fp.readlines()[:len(lines)]

        for attack in lines:
            attack_count += 1
            for team in teams:
                if attack and attack[-1] == "\n":
                    attack = attack[:-1]
                result = testprog.test_attack(team, testprog.attack_to_args(attack))
                result_str = "Failed"
                if result:
                    result_str = "Passed"
                    totals[team] += 1
                team_fps[team].write(result_str + " - '" + attack + "'\n")

        scoreboard_fp = open(self.CCTF_PATH+"/scoreboard.txt", 'w')
        for team in teams:
            scoreboard_fp.write(team+" "+str(totals[team])+"/"+str(attack_count)+"\n")

        data["teams"] = teams
        data["scores"] = totals
        data["total"] = attack_count
        json.dump(data, open(self.CCTF_PATH+"/scoreboard.json", 'w'))


#!/usr/bin/python

from score import Score
import os
import time
import requests
from git import Repo

RELOAD_TIME = 30  # Seconds
# HOME_PATH = os.getenv("HOME_PATH", "/cctf/server/attacks")
HOME_PATH = os.getenv("HOME_PATH", "server/attacks")
# CCTF_PATH = os.getenv("CCTF_PATH", "/cctf")
CCTF_PATH = os.getenv("CCTF_PATH", "")
TEAMS = []
BASE_URL = "http://127.0.0.1:5000"
def create_team_folders():
    for folder in os.listdir(HOME_PATH): #Get list of all directories in the upload directory (TEAM NAMES)
        if not os.path.exists(CCTF_PATH + '/attacks/' +  folder):
            os.makedirs(CCTF_PATH + '/attacks/' + folder)          #Create Team folder under attacks directory
        if not os.path.exists(CCTF_PATH + '/results/' +  folder):
            os.makedirs(CCTF_PATH + '/results/' + folder)         #Create Team folder under results directory

def check_teams():
    data = requests.get(url=BASE_URL+"/getAllTeams").json()
    print("TEAMS {}".format(data["teams"]))

if __name__ == '__main__':
    game = Score(HOME_PATH, CCTF_PATH, RELOAD_TIME)

    #Timed loop
    while True:
        check_teams()
        create_team_folders()

        start_time = time.time()

        # game.score()

        end_time = time.time()
        print("Reloaded Scoreboard @", time.ctime())
        elapsed_time = end_time - start_time
        if elapsed_time < RELOAD_TIME:
            time.sleep(RELOAD_TIME - elapsed_time)

#!/usr/bin/python

from score import Score
import os
import time
from git import Repo

RELOAD_TIME = 30  # Seconds
HOME_PATH = os.getenv("HOME_PATH", "/cctf/server/uploads")
CCTF_PATH = os.getenv("CCTF_PATH", "/cctf")

def create_team_folders():
    for folder in os.listdir(HOME_PATH): #Get list of all directories in the upload directory (TEAM NAMES)
        if not os.path.exists(CCTF_PATH + '/attacks/' +  folder):
            os.makedirs(CCTF_PATH + '/attacks/' + folder);          #Create Team folder under attacks directory
        if not os.path.exists(CCTF_PATH + '/results/' +  folder):
            os.makedirs(CCTF_PATH + '/results/' + folder);          #Create Team folder under results directory
        if not os.path.exists(CCTF_PATH + '/gitrepos/' + folder):   #Create Team folder repository
            #Initialize bare repo in gitrepos folder
            br = Repo.init(os.path.join(CCTF_PATH + '/gitrepos/', folder), bare=True)
            assert br.bare

if __name__ == '__main__':
    game = Score(HOME_PATH, CCTF_PATH, RELOAD_TIME)

    #Timed loop
    while True:
        create_team_folders()

        start_time = time.time()

        game.score()

        end_time = time.time()
        print("Reloaded Scoreboard @", time.ctime())
        elapsed_time = end_time - start_time
        if elapsed_time < RELOAD_TIME:
            time.sleep(RELOAD_TIME - elapsed_time)

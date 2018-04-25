#!/usr/bin/env python3
import os
import time
import requests
from git import Repo
from flask import Flask, request
from multiprocessing import Queue
from tasker import Tasker, Attack, Team
from manager import AttackManager

from config import PORT


app = Flask(__name__)
task_queue = Queue()


@app.route('/team/<team_name>')
def team(team_name):
    print("Team: {}".format(team_name))
    task_queue.put(Team(team_name))
    return "Good"


@app.route('/attack/<attack_name>')
def attack(attack_name):
    print("Attack: {}".format(attack_name))
    task_queue.put(Attack(attack_name))
    return "Good"


if __name__ == '__main__':
    print("Starting...")
    attack_manager = AttackManager()
    print("Loading existing attacks...")
    old_attacks = attack_manager.load_existing_attacks()
    t = Tasker(task_queue, attacks=old_attacks)
    t.start()
    app.run(host='127.0.0.1', port=PORT)
    task_queue.put(None)
    t.join()
    print("Dead.")


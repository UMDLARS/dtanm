#!/usr/bin/env python3

import logging
import sys
from redis import Redis
import os
from time import sleep
from datetime import datetime
import git
from sqlalchemy.exc import NoSuchTableError
import signal

from attack import Attack
from worker import Exerciser, Gold
from utils import are_dirs_same

sys.path.append('/pack')
import config

def score_against_gold(team_id: int, attack_id: int):
    attack_path = os.path.join('/cctf/attacks/', str(attack_id))

    with Exerciser(config.SCORING_BIN_NAME,
                    git_remote=os.path.join('/cctf/repos', str(team_id)),
                    attack=Attack(attack_path)) as team_exerciser:
        start_time = datetime.now()

        try:
            result = team_exerciser.run()

            gold_result = session.query(Result).filter(Result.gold == True).filter(Result.attack_id == attack_id).order_by(Result.created_at.desc()).first()
            if gold_result is None:

                with Gold(config.SCORING_GOLD_NAME,
                          gold_src="/pack/gold",
                          attack=Attack(attack_path)) as gold:
                    gold_result = gold.run()

                gold_result.attack_id = attack_id
                gold_result.gold = True
                gold_result.commit_hash = git.Repo.init('/pack/gold').head.commit.hexsha
                session.add(gold_result)
                session.commit()

        except Exception as e: # TODO: more precisely define what exceptions we may catch here
            result = Result()
            result.attack_id = attack_id
            result.team_id = team_id
            result.commit_hash = git.Repo.init(os.path.join('/cctf/repos', str(team_id))).head.commit.hexsha
            result.passed = False
            result.output = f"Scoring error: {e}"
            result.seconds_to_complete = (datetime.now() - start_time).seconds
            session.add(result)
            session.commit()
            return

        output = ""
        passed = True
        result.stdout_correct = result.stderr_correct = result.return_code_correct = result.filesystem_correct = True
        if True:# self.config.score_stdout:
            if result.stdout != gold_result.stdout:
                result.stdout_correct = False
                passed = False
        if True:# self.config.score_stderr:
            if result.stderr != gold_result.stderr:
                result.stderr_correct = False
                passed = False
        if True:# self.config.score_return_code:
            if result.return_code != gold_result.return_code:
                result.return_code_correct = False
                passed = False
        # if self.config.score_working_dir:
            # TODO: switch to hashing directories
            #if not are_dirs_same(result.directory, gold_result.directory):
            #    result.filesystem_correct = False
            #    passed = False

        result.attack_id = attack_id
        result.gold = False
        result.team_id = team_id
        result.commit_hash = git.Repo.init(os.path.join('/cctf/repos', str(team_id))).head.commit.hexsha
        result.passed = passed
        result.output = output
        session.add(result)
        session.commit()


# from https://stackoverflow.com/a/31464349
class SignalHandler:
    should_exit = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.should_exit = True


if __name__ == '__main__':
    redis =  Redis(host=os.environ.get('REDIS_HOST', 'localhost'),
                   port=os.environ.get('REDIS_PORT', 6379),
                   db=os.environ.get('REDIS_DB', 0))
    logging.basicConfig(level=logging.INFO)

    hostname = os.uname()[1]
    redis.sadd('workers', hostname)
    redis.sadd('idle-workers', hostname)

    # `web` has to populate the database first before we read the Result model
    while True:
        try:
            from result import Result, session
        except NoSuchTableError:
            logging.info("Database not ready, trying again.")
            sleep(1)
            continue
        break

    handler = SignalHandler()
    while not handler.should_exit:
        tasks = redis.zpopmin('tasks')
        if len(tasks) == 0:
            sleep(0.1)
            continue
        redis.srem('idle-workers', hostname)
        (task, priority) = tasks[0]
        task = str(task)
        logging.getLogger(__name__).info(f'Got task: {task}')
        (team_id, attack_id) = task.split('-')

        score_against_gold(team_id, attack_id)

        redis.sadd('idle-workers', hostname)

    logging.info('caught SIGINT or SIGTERM; exiting')
    redis.srem('workers', hostname)
    redis.srem('idle-workers', hostname)

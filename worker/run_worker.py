import logging
import sys
from redis import Redis
import os
from time import sleep
from datetime import datetime
import git

from attack import Attack
from result import Result, session
from worker import Exerciser, Gold
from utils import are_dirs_same

sys.path.append('/pack')
import config

def score(team_id: int, attack_id: int):
    attack_path = os.path.join('/cctf/attacks/', str(attack_id))
    with Exerciser(config.SCORING_BIN_NAME,
                    git_remote=os.path.join('/cctf/repos', str(team_id)),
                    attack=Attack(attack_path)) as team_exerciser, \
            Gold(config.SCORING_GOLD_NAME,
                    gold_src="/pack/gold",
                    attack=Attack(attack_path)) as gold:
        start_time = datetime.now()

        try:
            team_result = team_exerciser.run()
            gold_result = gold.run()
        except Exception as e: # TODO: more precisely define what exceptions we may catch here
            result = Result()
            result.attack_id = attack_id
            result.team_id = team_id
            result.commit_hash = git.Repo.init(os.path.join('/cctf/repos', str(team_id))).head.commit.hexsha
            result.passed = False
            result.output = f"Scoring error: {e}"
            result.start_time = start_time
            result.seconds_to_complete = (datetime.now() - start_time).seconds
            session.add(result)
            session.commit()
            return


        passed = True
        output = ""
        if True:# self.config.score_stdout:
            if team_result.stdout != gold_result.stdout:
                passed = False
                output += f"STDOUT: expected: {gold_result.stdout}, received: {team_result.stdout}\n"
        if True:# self.config.score_stderr:
            if team_result.stderr != gold_result.stderr:
                passed = False
                output += f"STDERR: expected: {gold_result.stderr}, received: {team_result.stderr}\n"
        if True:# self.config.score_exit_code:
            if team_result.exit_code != gold_result.exit_code:
                passed = False
                output += f"EXIT CODE: expected: {gold_result.exit_code}, received: {team_result.exit_code}\n"
        if False:# self.config.score_working_dir:
            if not are_dirs_same(team_result.directory, gold_result.directory):
                passed = False
                output += f"WORKING DIR: Files were different.\n"

        result = Result()
        result.attack_id = attack_id
        result.team_id = team_id
        result.commit_hash = team_result.commit_checksum
        result.passed = passed
        result.output = output
        result.start_time = start_time
        result.seconds_to_complete = team_result.time_sec + gold_result.time_sec
        session.add(result)
        session.commit()

if __name__ == '__main__':
    redis =  Redis(host=os.environ.get('REDIS_HOST', 'localhost'),
                   port=os.environ.get('REDIS_PORT', 6379),
                   db=os.environ.get('REDIS_DB', 0))
    logging.basicConfig(level=logging.INFO)

    hostname = os.uname()[1]
    redis.sadd('workers', hostname)
    redis.sadd('idle-workers', hostname)

    while True:
        (queue, task, priority) = redis.bzpopmin('tasks')
        task = task.decode()
        if task is None:
            sleep(0.1)
            continue
        redis.srem('idle-workers', hostname)
        logging.getLogger(__name__).info(f'Got task: {task}')
        (team_id, attack_id) = task.split('-')
        score(team_id, attack_id)
        redis.sadd('idle-workers', hostname)

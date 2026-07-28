#!/usr/bin/env python3

import logging
import sys
from redis import Redis
import os
from time import sleep, time
from datetime import datetime
from dulwich.repo import Repo
from dulwich.errors import NotGitRepository
import dulwich.porcelain as git
from sqlalchemy.exc import IntegrityError, NoSuchTableError, OperationalError
from sqlalchemy import select
import signal
import traceback
from packaging.version import Version

from attack import Attack
from utils import are_dirs_same

sys.path.append('/cctf/pack')

redis = None

MIN_SUPPORTED_PACK_VER = Version("3.0")
MAX_SUPPORTED_PACK_VER = Version("4.0")

pack_version = None

def get_gold_score_path():
    if pack_version < Version('4.0'):
        return config.SCORING_GOLD_NAME
    else:
        return config.SCORING_BIN_NAME

def get_gold_commit_hash():
    # set gold_commit_hash
    try: # see if gold has its own repo
        gold_commit_hash = Repo('/cctf/pack/gold').head().decode()
    except NotGitRepository:
        try: # fall back to the pack repo
            gold_commit_hash = Repo('/cctf/pack').head().decode()
        except NotGitRepository: # no repos here! default to emptystring.
            gold_commit_hash = ""
            # TODO: in theory we could create some sort of hash here
            # ourselves, potentially simply an md5sum of the contents of
            # `gold` or something like that.
        except KeyError: # b'HEAD' not found
            logging.log("/cctf/pack has a git repo but no commits")
            gold_commit_hash = ""
    except KeyError: # b'HEAD' not found
        logging.log("/cctf/pack/gold has a git repo but no commits")
        gold_commit_hash = ""
    return gold_commit_hash

def score_gold(attack_id: int):
    from worker import GoldExerciser
    import config
    attack_path = os.path.join('/cctf/attacks/', str(attack_id))

    with GoldExerciser(get_gold_score_path(),
              pack_path="/cctf/pack",
              attack=Attack(attack_path)) as gold:
        gold_result = gold.run()

    gold_result.attack_id = attack_id
    gold_result.gold = True
    gold_result.commit_hash = get_gold_commit_hash()
    logging.getLogger(__name__).info(f"gold result: {gold_result}")
    session.add(gold_result)
    try:
        session.commit()
    except IntegrityError as e:
        # Catch if an attack with scoring in-progress has been deleted
        logging.exception(e)
        logging.info('Rolling back database session and discarding current result')
        session.rollback()
        return
    
def add_team_score_tasks(attack_id: str):
    for team_id in session.scalars(select(Team.id)):
        redis.zadd('tasks', {f"t.{team_id}-{attack_id}": time()})

def score_against_gold(team_id: str, attack_id: str):
    from worker import UserExerciser
    import config
    attack_path = os.path.join('/cctf/attacks/', str(attack_id))

    with UserExerciser(config.SCORING_BIN_NAME,
                    git_remote=os.path.join('/cctf/repos', str(team_id)),
                    attack=Attack(attack_path)) as team_exerciser:
        start_time = datetime.now()

        try:
            result = team_exerciser.run()

            # set gold_commit_hash
            gold_commit_hash = get_gold_commit_hash()

            gold_result = session.query(Result).filter(Result.gold == True).filter(Result.attack_id == attack_id).order_by(Result.created_at.desc()).first()
            if gold_result is None or gold_result.commit_hash != gold_commit_hash:
                raise Exception() # TODO: what should this be?
        except Exception as e: # TODO: more precisely define what exceptions we may catch here
            result = Result()
            result.attack_id = attack_id
            result.team_id = team_id
            result.commit_hash = Repo(os.path.join('/cctf/repos', str(team_id))).head().decode()
            result.passed = False
            result.output = f"Scoring error: {e}"
            logging.exception(e)
            result.seconds_to_complete = (datetime.now() - start_time).seconds
            session.add(result)
            try:
                session.commit()
            except IntegrityError as e:
                # Catch if an attack with scoring in-progress has been deleted
                logging.exception(e)
                logging.info('Rolling back database session and discarding current result')
                session.rollback()
                return
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
        result.commit_hash = Repo(os.path.join('/cctf/repos', str(team_id))).head().decode()
        result.passed = passed
        result.output = output
        logging.getLogger(__name__).info(f"result: {result}")
        session.add(result)
        try:
            session.commit()
        except IntegrityError as e:
            # Catch if an attack with scoring in-progress has been deleted
            logging.exception(e)
            logging.info('Rolling back database session and discarding current result')
            session.rollback()
            return


# from https://stackoverflow.com/a/31464349
class SignalHandler:
    should_exit = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.should_exit = True


if __name__ == '__main__':
    print("worker init 1", flush=True)

    logging.basicConfig(level=logging.INFO)

    try:
        redis = Redis(host=os.environ.get('REDIS_HOST', 'localhost'),
                        port=os.environ.get('REDIS_PORT', 6379),
                        db=os.environ.get('REDIS_DB', 0))

        logging.info("worker init")

        # `web` has to populate the database first before we read the Result model
        while True:
            try:
                from db import Result, Team, session
                import config
            except NoSuchTableError, OperationalError:
                logging.info("Database not ready, trying again.")
                sleep(1)
                continue
            break

        try:
            pack_ver_str = config.PACK_FORMAT_VERSION
        except:
            pack_ver_str = '3.0'
        
        pack_version = Version(pack_ver_str)
        if pack_version < MIN_SUPPORTED_PACK_VER or pack_version > MAX_SUPPORTED_PACK_VER:
            logging.error(f'Unsupported pack format version: {pack_version}')
            logging.error(f'Min Supported Version: {str(MIN_SUPPORTED_PACK_VER)}')
            logging.error(f'Max Supported Version: {str(MAX_SUPPORTED_PACK_VER)}')
            sys.exit(-1)
        else:
            logging.info(f'Pack Format Version: {str(pack_version)}')


        hostname = os.uname()[1]
        redis.sadd('workers', hostname)
        redis.sadd('idle-workers', hostname)
    except Exception as e:
        logging.error(f'Caught error during startup; exiting: {e}')
        logging.exception(e)
        redis.srem('workers', hostname)
        redis.srem('idle-workers', hostname)
        sys.exit(-1)

    """
    Task format:
    Tasks submissions are a plaintext strings. They are formatted as '{spec}.{args}',
    where spec species the task type and args specifies any arguments 

    The following task types are recognized:
        - 'a.{attack_id}' - tests an attack against gold then against all team programs
        - 't.{team_id}-{attack_id}' - tests an attack against a team's program
        - 'g.{attack_id}' - tests an attack against gold

    """
    handler = SignalHandler()
    while not handler.should_exit:
        tasks = redis.zpopmin('tasks')

        if len(tasks) == 0:
            sleep(0.1)
            continue
        redis.srem('idle-workers', hostname)

        try:
            (task, priority) = tasks[0]
            task: str = task.decode()
            logging.info(f'Got task: {task}')
            (spec, args) = task.split('.', 1)
            if spec == 'a':
                attack_id = args
                if not attack_id.isdigit():
                    raise Exception(f"invalid attack_id: {attack_id}")
                score_gold(attack_id)
                add_team_score_tasks(attack_id)
            elif spec == 't':
                (team_id, attack_id) = args.split('-')
                if not team_id.isdigit():
                    raise Exception(f"invalid team_id: {team_id}")
                elif not attack_id.isdigit():
                    raise Exception(f"invalid attack_id: {attack_id}")
                score_against_gold(team_id, attack_id)
            elif spec == 'g':
                attack_id = args
                if not attack_id.isdigit():
                    raise Exception(f"invalid attack_id: {attack_id}")
                score_gold(attack_id)
            else:
                logging.warning(f'unknown task type: {spec}')
        except Exception as e:
            logging.warning(f'Caught command error; ignoring: {e}')
            logging.warning(traceback.format_exc())
            pass

        logging.info(f'finished task: {task}')

        redis.sadd('idle-workers', hostname)

    logging.info('caught SIGINT or SIGTERM; exiting')
    redis.srem('workers', hostname)
    redis.srem('idle-workers', hostname)


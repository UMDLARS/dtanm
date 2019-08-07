#!/usr/bin/env python3

import json
import os
import shutil
import tempfile
import time
import logging
from time import sleep
from multiprocessing import Process
from subprocess import Popen, PIPE
from typing import Optional

from redis import Redis

import git

from attack import Attack
from result import Result
from team import Team
from utils import are_dirs_same, Timer

from result import Result, session


class ExerciseResults:
    stdout: bytes
    stderr: bytes
    exit_code: int
    directory: str
    time_sec: float
    commit_checksum: Optional[str]

    def __init__(self, stdout, stderr, exit_code, directory, time_sec, commit_checksum=None):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.directory = directory
        self.time_sec = time_sec
        self.commit_checksum = commit_checksum


class Exerciser:
    TIMEOUT = 1
    LOOP_TIME = 0.002

    def __init__(self, prog: str, attack: Attack, git_remote: str = None, src_path: str = None):
        """

        Args:
            prog: A relative path from the source directory to the program.
            args:
            stdin:
            env_dir:
            git_remote:
        """
        self.prog = prog
        self.args = attack.cmd_args
        self.stdin_file = attack.stdin_filepath
        self.env_dir = attack.env

        assert git_remote or src_path, \
            "Either the source directory must be passed or the git remote."
        assert not (git_remote and src_path), \
            "Git remote and source directory can't be set at the same time."
        self.git_remote = git_remote
        self.src_path = src_path

        self.repo = None

    def __enter__(self):
        self.exercise_dir = tempfile.mkdtemp()
        self.working_dir = os.path.join(self.exercise_dir, "env")
        self.source_dir = os.path.join(self.exercise_dir, "src")

        if self.env_dir:
            shutil.copytree(self.env_dir, self.working_dir)
        else:
            os.mkdir(self.working_dir)

        if self.git_remote:
            self.repo = git.Repo.init(self.source_dir)
            self.repo.create_remote("origin", self.git_remote).pull("refs/heads/master")
        elif self.src_path:
            self.source_dir = self.src_path
        return self

    def __exit__(self, *args):
        shutil.rmtree(self.exercise_dir)

    def get_repo_checksum(self) -> Optional[str]:
        if self.repo:
            return self.repo.head.commit.hexsha

    def run(self) -> Optional[ExerciseResults]:
        with open(self.stdin_file, "rb") as fp, Timer() as timer:
            try:
                process = Popen([os.path.join(self.source_dir, self.prog)] + self.args,
                                stdin=fp,
                                stdout=PIPE,
                                stderr=PIPE,
                                cwd=self.working_dir)
            except FileNotFoundError:
                raise FileNotFoundError("The executable could not be found.")

            start_time = time.time()
            exit_code = process.poll()
            while exit_code is None:
                time.sleep(Exerciser.LOOP_TIME)
                exit_code = process.poll()
                if time.time() - start_time > Exerciser.TIMEOUT:
                    process.kill()
                    print("User's program was killed.")
                    return

            out, err = process.communicate()

        return ExerciseResults(out, err, exit_code, self.working_dir, timer.interval, self.get_repo_checksum())


class Gold(Exerciser):
    # TODO: change this to cache results.
    def __init__(self, prog: str, gold_src: str, attack: Attack):
        super().__init__(prog, attack, git_remote=None, src_path=gold_src)


class ScoringConfig:
    def __init__(self, bin_name, gold_name, gold_dir):
        self.bin_name = bin_name
        self.gold_name = gold_name
        self.gold_dir = gold_dir

        self.score_stdout = True
        self.score_stderr = True
        self.score_exit_code = True
        self.score_working_dir = True


class ScoreResult:
    team: Team
    attack: Attack
    passed: bool
    commit: str

    def __init__(self, team: Team, attack: Attack, passed: bool, team_sec: float, gold_sec: float, commit: str):
        self.team = team
        self.attack = attack
        self.passed = passed
        self.commit = commit
        self.team_sec = team_sec
        self.gold_sec = gold_sec
        self.start_time = time.time()
        self.log = logging.getLogger(__name__)

    def make_result_id(self):
        return f'{self.team.id}-{self.commit}-{self.attack.id}'

    def make_audit_log_id(self):
        return f'{self.team.id}-{self.commit}-{self.attack.id}-{self.start_time}'

    def save(self):
        res = Result()
        res.attack = self.attack.id
        res.team = self.team.id
        res.commit = self.commit
        res.passed = self.passed

        try:
            res.save()
        except NotUniqueError as ex:
            self.log.warning(f'Scored team, attack pair twice!!! Exception: {ex}')
            res = Result.objects(attack=res.attack, team=res.team, commit=res.commit)[0]
            res.passed = self.passed
            res.save()

        audit_rec = AuditLog()
        audit_rec.result = res
        audit_rec.attack = self.attack.id
        audit_rec.team = self.team.id
        audit_rec.commit = self.commit
        audit_rec.passed = self.passed
        audit_rec.start_time = self.start_time
        audit_rec.team_time_sec = self.team_sec
        audit_rec.gold_time_sec = self.gold_sec

        audit_rec.save()

    # def save(self, directory):
    #     with open(f"{directory}/{self.team.name}_{self.attack.name}.json", "w") as fp:
    #         json.dump({"passed": self.passed,
    #                    "team_sec": self.team_sec,
    #                    "gold_sec": self.gold_sec,
    #                    "commit": self.commit}, fp)


class Scorer(Process):
    def __init__(self, config: ScoringConfig,
                 redis: Redis):
        self.config = config
        self.redis = redis
        self.log = logging.getLogger(__name__)
        super().__init__()

    def run(self):
        try:
            while True:
                (queue, task, priority) = self.redis.bzpopmin('tasks')
                task = task.decode()
                if task is None:
                    sleep(0.1)
                    continue
                self.log.info(f'Got task: {task}')
                (team_id, attack_id) = task.split('-')
                res = self.score(team_id, attack_id)
                result = Result()
                result.attack_id = attack_id
                result.team_id = team_id
                result.commit_hash = res.commit
                result.passed = res.passed
                result.output = "nice" if res.passed else "darn"
                # start_time = datetime.datetime.now()
                # seconds_to_complete = 0
                session.add(result)
                session.commit()

        except KeyboardInterrupt:
            # TODO: clean up running child processes.
            pass

        self.log.info("Scorer Process dying...")

    def score(self, team_id: int, attack_id: int) -> ScoreResult:
        attack_path = os.path.join('/cctf/attacks/', str(attack_id))
        with Exerciser(self.config.bin_name,
                       git_remote=os.path.join('/cctf/repos', str(team_id)),
                       attack=Attack(attack_path)) as team_exerciser, \
                Gold(self.config.gold_name,
                     self.config.gold_dir,
                     attack=Attack(attack_path)) as gold:
            team_result = team_exerciser.run()
            gold_result = gold.run()

            passed = True

            if self.config.score_stdout:
                if team_result.stdout != gold_result.stdout:
                    passed = False
            if self.config.score_stderr:
                if team_result.stdout != gold_result.stdout:
                    passed = False
            if self.config.score_exit_code:
                if team_result.exit_code != gold_result.exit_code:
                    passed = False
            if self.config.score_working_dir:
                if not are_dirs_same(team_result.directory, gold_result.directory):
                    passed = False

            return ScoreResult(team=team_id,
                               attack=attack_id,
                               passed=passed,
                               team_sec=team_result.time_sec,
                               gold_sec=gold_result.time_sec,
                               commit=team_result.commit_checksum)

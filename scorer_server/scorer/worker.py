#!/usr/bin/env python3
from __future__ import print_function

import os
import shutil
import tempfile
import time
from multiprocessing import Process, Queue
from subprocess import Popen, PIPE
from typing import Optional

import git

from scorer.attack import Attack
from scorer.tasks import ScoreTask
from scorer.team import Team
from scorer.utils import are_dirs_same


class ExerciseResults:
    stdout: bytes
    stderr: bytes
    exit_code: int
    directory: str

    def __init__(self, stdout, stderr, exit_code, directory):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.directory = directory


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

    def get_repo_checksum(self):
        return self.repo.head.commit.hexsha

    def run(self) -> Optional[ExerciseResults]:
        with open(self.stdin_file, "rb") as fp:
            process = Popen([os.path.join(self.source_dir, self.prog)] + self.args,
                            stdin=fp,
                            stdout=PIPE,
                            stderr=PIPE,
                            cwd=self.working_dir)

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

            return ExerciseResults(out, err, exit_code, self.working_dir)


class Gold(Exerciser):
    # TODO: change this to cache results.
    def __init__(self, prog: str, gold_src: str, attack: Attack):
        super().__init__(prog, attack, git_remote=None, src_path=gold_src)


class ScoringConfig:
    def __init__(self, bin_name, gold_name, gold_src):
        self.bin_name = bin_name
        self.gold_name = gold_name
        self.gold_src = gold_src

        self.score_stdout = True
        self.score_stderr = True
        self.score_exit_code = True
        self.score_working_dir = True


class ScoreResult:
    team: Team
    attack: Attack
    passed: bool
    commit: str

    def __init__(self, team: Team, attack: Attack, passed: bool, commit: str):
        self.team = team
        self.attack = attack
        self.passed = passed
        self.commit = commit

    def submit(self):
        print("Submitting ScoreResult:")
        print(f"  Team:   {self.team}")
        print(f"  Attack: {self.attack}")
        print(f"  Passed: {self.passed}")
        print(f"  Commit: {self.commit}")


class Scorer(Process):
    def __init__(self, queue: Queue, config: ScoringConfig):
        self.queue = queue
        self.config = config
        super().__init__()

    def run(self):
        try:
            while 1:
                task = self.queue.get()
                if task is None:
                    break
                res = self.score(task)
                if res:
                    res.submit()

        except KeyboardInterrupt:
            # TODO: clean up running child processes.
            pass

        print("Scorer Process dying...")

    def score(self, task: ScoreTask) -> ScoreResult:
        print("Scoring: {}".format(task))

        with Exerciser(self.config.bin_name,
                       attack=task.attack,
                       git_remote=task.team.get_git_remote()) as team_exerciser, \
                Gold(self.config.gold_name,
                     self.config.gold_src,
                     attack=task.attack) as gold:
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
                if are_dirs_same(team_result.directory, gold_result.directory):
                    passed = False

            return ScoreResult(team=task.team,
                               attack=task.attack,
                               passed=passed,
                               commit=team_result.get_repo_checksum())

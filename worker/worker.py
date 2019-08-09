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

from datetime import datetime

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
            makefile_exists = os.path.isfile(os.path.join(self.source_dir, "Makefile"))
            makefile_error = None
            if makefile_exists:
                try:
                    process = Popen("make",
                                    stdout=PIPE,
                                    stderr=PIPE,
                                    cwd=self.source_dir).wait()
                    # Todo: catch make errors
                    print(os.listdir(self.working_dir))
                except Exception as e:
                    makefile_error = e

            try:
                process = Popen([os.path.join(self.source_dir, self.prog)] + self.args,
                                stdin=fp,
                                stdout=PIPE,
                                stderr=PIPE,
                                cwd=self.working_dir)
            except FileNotFoundError:
                if not makefile_exists:
                    raise FileNotFoundError("Neither the executable nor a valid makefile could be found")
                elif makefile_error is not None:
                    raise FileNotFoundError(f"The makefile could not be run ({str(makefile_error)}), and no valid executable was found.")
                else:
                    raise FileNotFoundError(f"The makefile ran successfully but no {self.prog} could be found.")


            start_time = time.time()
            exit_code = process.poll()
            while exit_code is None:
                time.sleep(Exerciser.LOOP_TIME)
                exit_code = process.poll()
                if time.time() - start_time > Exerciser.TIMEOUT:
                    process.kill()
                    raise Exception("The program took too long and was killed.")

            out, err = process.communicate()

        return ExerciseResults(out.decode(), err.decode(), exit_code, self.working_dir, timer.interval, self.get_repo_checksum())


class Gold(Exerciser):
    # TODO: change this to cache results.
    def __init__(self, prog: str, gold_src: str, attack: Attack):
        super().__init__(prog, attack, git_remote=None, src_path=gold_src)

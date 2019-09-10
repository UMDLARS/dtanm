#!/usr/bin/env python3

import os
import shutil
import tempfile
import time
from subprocess import Popen, PIPE
from typing import Optional
import git
from docker_runner import DockerRunner, DockerTimeoutException

from attack import Attack
from utils import Timer


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
    TIMEOUT = 10
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
        else
            return "gold"

    def run(self) -> Optional[ExerciseResults]:
        client = docker.from_env()

        docker_image_name = self.get_repo_checksum()

        # Build Docker image of the program
        try:
            base_docker_image = client.images.get(docker_image_name)
        except docker.errors.ImageNotFound as e:
            shutil.copyfile('/pack/Dockerfile.build', os.path.join(self.source_dir, "Dockerfile"))
            base_docker_image = client.images.build(path=self.source_dir, tag=self.get_repo_checksum())

        # Build Docker image of the attack
        with open(os.path.join(self.source_dir, "Dockerfile"), 'w') as f:
            f.write((f"FROM {docker_image_name}"
                     "WORKDIR /usr/src/dtanm/env"
                     "COPY . ."
                     "ENTRYPOINT /bin/bash" # this was overridden in the intermediate Dockerfile
                     f"CMD ./{self.prog} {' '.join(self.args)}"
            ))
        docker_image = client.images.build(path=self.source_dir)

        # run Docker image of the attack
        container = client.containers.create(docker_image,
                                             self.cmd,
                                             mem_limit=self.MEMORY_LIMIT,
                                             pids_limit=self.PIDS_LIMIT,
                                             cpu_period=self.CPU_PERIOD,
                                             cpu_quota=int(self.CPU_PERIOD * self.CPUS),
                                             tmpfs={'/foo': f'size={self.MAX_DISK},exec'},
                                             detach=True, )  # type: Container


        with open(self.stdin_file, "rb") as fp, Timer() as timer:
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
                    print("The program took too long and was killed.")

            out, err = process.communicate()

        return ExerciseResults(out.decode(), err.decode(), exit_code, self.working_dir, timer.interval, self.get_repo_checksum())


class Gold(Exerciser):
    # TODO: change this to cache results.
    def __init__(self, prog: str, gold_src: str, attack: Attack):
        super().__init__(prog, attack, git_remote=None, src_path=gold_src)

import os
import shutil
import tempfile
import time
from subprocess import Popen, PIPE
from typing import Optional
from dulwich import porcelain
from dulwich.repo import Repo
from dulwich.errors import NotGitRepository
import docker
import logging
import requests
import random

from pathlib import Path

from attack import Attack
from db import Result

import sys
sys.path.append('/cctf/pack')

class ExerciserImpl:
    TIMEOUT = 10
    LOOP_TIME = 0.002

    def __init__(self, prog: str, attack: Attack):
        self.prog = prog
        self.args = attack.cmd_args
        #self.stdin_file = attack.stdin_filepath
        self.files_dir = attack.files
        self.envs = attack.env

        if self.files_dir and not os.path.realpath(attack).startswith('/cctf/attacks'):
            raise Exception(f'Invalid attack files directory: {os.path.realpath(attack)}')

    def _setup_dirs_impl(self):
        # Create a temp dir to store the program src in. 
        self.source_dir = tempfile.mkdtemp()

        # Setup the args_store directory in the args_store volume.
        while True:
            self.args_subdir = f"{os.uname()[1]}_{random.getrandbits(32)}" # device hostname
            self.args_dir = os.path.join('/args_store', self.args_subdir)
            try:
                os.mkdir(self.args_dir)
                break
            except FileExistsError:
                pass
        
        # Setup the directory the program will be run in and copy over any attack files.
        self.working_dir = os.path.join(self.args_dir, 'work')
        if self.files_dir:
            shutil.copytree(self.files_dir, self.working_dir, symlinks=True)
        else:
            os.mkdir(self.working_dir)

    def __exit__(self, *args):
        shutil.rmtree(self.source_dir)
        shutil.rmtree(self.exercise_dir)
        shutil.rmtree(self.args_dir)

    def run(self) -> Result:
        import config
        client = docker.from_env()

        docker_image_name = self._get_container_name()

        # Build Docker image of the program
        try:
            base_docker_image = client.images.get(docker_image_name)
        except docker.errors.ImageNotFound as e:
            # Determine where the dockerfile is and copy it to our work dir.
            dockerfile_path = os.path.join(self.source_dir, "Dockerfile")
            shutil.copyfile('/cctf/pack/Dockerfile.build', dockerfile_path)

            # Setup an xargs command to run the program with args from a file.
            # Honestly don't remember how this works, but I had to do some funky stuff to get the proper return value out.
            with open(dockerfile_path, 'a') as f:
                # ref: https://stackoverflow.com/questions/28080307/either-getting-original-return-value-from-xargs-or-simulate-xargs
                chgdir = 'WORKDIR /opt/dtanm/env/work\n'
                f.write(chgdir)
                entrypoint = f"ENTRYPOINT xargs bash -c '{ os.path.join('/opt/dtanm', self.prog) } \"$@\"; echo $? > /opt/dtanm/env/retval' - < /opt/dtanm/env/args\n"
                f.write(entrypoint)
            
            # Run the dockerfile to build the testing container
            base_docker_image, logs = client.images.build(path=self.source_dir, tag=docker_image_name)
            logging.getLogger(__name__).info("built dockerfile: " + base_docker_image.id)

        # Write the program arguments to /args_store/
        with open(os.path.join(self.args_dir, 'args'), 'w') as f:
            f.write(f"{self.args.decode()}")

        # Grab the environment vars we want to run the program with.
        with open(self.envs) as f:
            env_vars = [line.rstrip() for line in f.readlines()]

        # Setup volume mount to mount our args_store subdir as /opt/dtanm/env.
        # NOTE: subpath stuff depends on docker-py git
        args_mount = docker.types.Mount(type="volume", target="/opt/dtanm/env", source="dtanm_args_store", subpath=self.args_subdir)

        # Create a docker container for the program/attack.
        container = client.containers.create(image=docker_image_name,
                                             #command=self.cmd, # The command is in the Dockerfile
                                             mem_limit=config.SCORING_MAX_MEMORY,
                                             pids_limit=config.SCORING_MAX_PROCESSES,
                                             environment=env_vars,
                                             cpu_period=10000,
                                             cpu_quota=int(10000 * config.SCORING_MAX_CPUS),
                                             detach=True,
                                             network_disabled=getattr(config, "SCORING_DISABLE_NETWORK", True),
                                             mounts=[args_mount])

        # Record start time.
        start_time = time.time()

        # Let 'er rip
        container.start()

        # (try to) wait until the test finishes.
        try:
            results = container.wait(timeout=config.SCORING_MAX_TIME)

            # Record the elapsed time.
            elapsed_time = time.time() - start_time # Originally time.perf_counter was used here. Perhaps that would be a better option in the future?
            
            # Try to grab the return code, use an impossible(?) default if the retval file is missing.
            try:
                return_code = int(open(os.path.join(self.args_dir, "retval")).read())
            except:
                return_code = 0x7FFFFFFF # default to smth normally impossible
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):  # They timed out.
            # Stop + remove the container if it timed out.
            try:
                container.stop()
            except:
                pass
            try:
                container.remove(force=True)
            except:
                pass
            raise TimeoutError(f"Your process ran longer than the allowed { config.SCORING_MAX_TIME } seconds.")

        # Grab the stdout and stderr logs.
        stdout = container.logs(stdout=True, stderr=False)
        stderr = container.logs(stdout=False, stderr=True)

        # Cleanup the container, we don't need it anymore.
        try:
            container.remove(force=True)
        except:
            pass # TODO

        # Setup a result from the test outputs.
        result = Result()
        result.commit_hash = self._get_container_name()
        result.stdout = stdout
        result.stderr = stderr
        # TODO: add fs hash
        # result.filesystem_hash = ...
        result.return_code = return_code
        result.seconds_to_complete = elapsed_time
        return result

# User programs must be a git remote
class UserExerciser(ExerciserImpl):
    def __init__(self, prog: str, attack: Attack, git_remote: str = None):
        super().__init__(prog, attack)

        self.git_remote = git_remote
        self.repo = None

    def _get_container_name(self):
        return self.commit_hash

    def __enter__(self):
        # Setup work and src dirs.
        self._setup_dirs_impl()

        # Clone the team's program repo.
        self.repo = porcelain.clone(self.git_remote, self.source_dir)
        try:
            self.commit_hash = self.repo.head().decode()
        except KeyError as e:
            raise e # TODO log smth
        return self

# Gold programs are inside a pack that are optionally from a git repo.
class GoldExerciser(ExerciserImpl):
    def __init__(self, prog: str, attack: Attack, pack_path: str = None):
        # Initialize our base with the program/attack info.
        super().__init__(prog, attack)
        self.pack_path = pack_path

        # Check if the pack is in a git repo.
        try:
            self.repo = Repo(pack_path)
            self.commit_hash = self.repo.head().decode()
        except (NotGitRepository, KeyError):
            # If it's not a git repo, assign the default "gold" name.
            self.repo = None
            self.commit_hash = "gold"

    def _get_container_name(self):
        if self.repo:
            return self.repo.head().decode()
        else:
            return "gold"

    def __enter__(self):
        # Setup work and src dirs.
        self._setup_dirs_impl()

        # Copy the gold program to the source work dir.
        shutil.copytree(os.path.join(self.pack_path, 'gold'), self.source_dir, dirs_exist_ok=True)
        self.source_dir = os.path.join(self.pack_path, "gold")
        return self


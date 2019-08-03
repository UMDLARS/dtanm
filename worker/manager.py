from __future__ import print_function

import hashlib
import io
import os
import shutil
import tarfile
import tempfile
from typing import Optional

from attack import Attack
from team import Team


def hash_stream(fp):
    BUF_SIZE = 65536
    sha = hashlib.sha512()
    while True:
        data = fp.read(BUF_SIZE)
        if not data:
            break
        sha.update(data)
    return sha.hexdigest()


def is_valid_attack_tar(attack_tar):
    has_cmd_args = has_stdin = has_env = False
    for member in attack_tar.getmembers():
        if member.path[0] == '/':
            return False
        elif '..' in member.path:
            return False
        if member.path == "cmd_args" and member.isreg():
            has_cmd_args = True
        if member.path == "stdin" and member.isreg():
            has_stdin = True
        if member.path == "env" and member.isdir():
            has_env = True
    return has_cmd_args and has_stdin and has_env


def get_hash_for_attack_dir(attack_dir, subpath="."):
    buf = io.BytesIO()
    for f in sorted(os.listdir(os.path.join(attack_dir, subpath))):
        path = os.path.join(attack_dir, subpath, f)
        if os.path.isfile(path):
            with open(path, "rb") as fp:
                buf.write(bytes(os.path.join(subpath, f) + hash_stream(fp), encoding="utf-8"))
        elif os.path.isdir(path):
            buf.write(bytes(os.path.join(subpath, f) + get_hash_for_attack_dir(attack_dir, os.path.join(subpath, f)),
                            encoding="utf-8"))

    buf.seek(0)
    return hash_stream(buf)


def extract_tar(tf, out_dir):
    # TODO: update this function to allow for directories and non_flat attacks
    for member in tf.getmembers():
        if member.isdir():
            os.makedirs(os.path.join(out_dir, member.path), exist_ok=True)
    for member in tf.getmembers():
        if member.isreg():
            with open(os.path.join(out_dir, member.path), "wb") as fp:
                fp.write(tf.extractfile(member).read())


class TeamManager:
    def __init__(self, team_dir):
        self.team_dir = team_dir

    def process_team(self, team_name: str) -> Optional[Team]:
        team_path = os.path.join(self.team_dir, team_name)
        if not os.path.exists(team_path):
            print("Couldn't process team: '{}'. Couldn't find it.".format(team_name))
            return

        return Team(team_path)

    def team_from_id(self, team_id: str) -> Team:
        team_path = os.path.join(self.team_dir, team_id)
#        assert os.path.exists(team_path), "Team doesn't exist"
        return Team(team_path)


class AttackManager:
    def __init__(self, upload_dir, attacks_dir):
        self.attacks = set()
        self.upload_dir = upload_dir
        self.attacks_dir = attacks_dir

    def load_existing_attacks(self):
        for attack in os.listdir(self.attacks_dir):
            directory = os.path.join(self.attacks_dir, attack)
            attack_hash = get_hash_for_attack_dir(directory)
            assert attack == attack_hash, "Hashing method has changed!!! Rebuild Attack DB."
            self.attacks.add(Attack(os.path.join(self.attacks_dir, directory)))
        return self.attacks

    def attack_from_id(self, attack_id: str) -> Attack:
        attack_path = os.path.join(self.attacks_dir, attack_id)
#        assert os.path.exists(attack_path), "Attack doesn't exist"
        return Attack(attack_path)

    def process_attack(self, attack_name: str) -> Optional[Attack]:
        """
           This function takes an attack_name and if it is valid and unique returns its new name.
        """
        attack_path = os.path.join(self.upload_dir, attack_name)
        if not os.path.exists(attack_path):
            print("Couldn't process attack: '{}'. Couldn't find it.".format(attack_name))
            return

        with tarfile.open(attack_path, "r") as tf:
            if is_valid_attack_tar(tf):
                attack_dir = tempfile.mkdtemp()
                extract_tar(tf, attack_dir)
                attack_hash = get_hash_for_attack_dir(attack_dir)
                if attack_hash not in self.attacks:
                    dest = os.path.join(self.attacks_dir, attack_hash)
                    shutil.move(attack_dir, dest)
                    attack = Attack(dest)
                    self.attacks.add(attack)
                    return attack
                else:
                    print("Not processing duplicate attack: {}".format(attack_name))
            else:
                print("Invalid attack: '{}'".format(attack_name))
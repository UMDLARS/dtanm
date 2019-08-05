from __future__ import print_function

import hashlib
import io
import os
import shutil
import tarfile
import tempfile
from typing import Optional
from flask import g, current_app
from tarfile import TarFile

from web.scorer.attack import Attack
from web.scorer.team import Team


def hash_stream(fp):
    BUF_SIZE = 65536
    sha = hashlib.sha512()
    while True:
        data = fp.read(BUF_SIZE)
        if not data:
            break
        sha.update(data)
    return sha.hexdigest()


def is_valid_attack_tar(attack_tar: TarFile):
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


def get_team_manager():
    if 'team_manager' not in g:
        g.team_manager = TeamManager(team_dir=current_app.config["TEAM_DIR"])

    return g.team_manager


def get_attack_manager():
    if 'attack_manager' not in g:
        g.attack_manager = AttackManager(upload_dir=current_app.config["UPLOAD_DIR"],
                                             attacks_dir=current_app.config["ATTACKS_DIR"])

    return g.attack_manager

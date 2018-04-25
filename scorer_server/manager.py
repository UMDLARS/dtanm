from __future__ import print_function
import os
import sys
import time
import hashlib
import shutil
import tarfile
import tempfile
import io

from config import UPLOAD_DIR, ATTACK_DIR


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
    for member in attack_tar.getmembers():
        if member.path[0] == '/':
            return False
        elif '..' in member.path:
            return False
    return True


def get_hash_for_attack_dir(attack_dir):
    buf = io.BytesIO()
    for f in sorted(os.listdir(attack_dir)):
        path = os.path.join(attack_dir, f)
        if os.path.isfile(path):
            with open(path, "rb") as fp:
                buf.write(path + hash_stream(fp), encoding="utf-8")
        elif os.path.isdir(path):
            buf.write(path + get_hash_for_attack_dir(path), encoding="utf-8")

    buf.seek(0)
    return hash_stream(buf)


def extract_tar(tf, out_dir):
    # TODO: update this function to allow for directories and non_flat attacks
    for member in tf.getmembers():
        if member.isreg():
            with open(os.path.join(out_dir, os.path.basename(member.name)), "wb") as fp:
                fp.write(tf.extractfile(member))


class AttackManager:
    def __init__(self):
        self.attacks = {}

    def load_existing_attacks(self):
        for attack_name in os.listdir(ATTACK_DIR):
            self.attacks[attack_name] = get_hash_for_attack_dir(os.path.join(ATTACK_DIR, attack_name))
        return self.attacks.keys()

    def process_attack(self, attack_name):
        if attack_name in self.attacks:
            print("Attack by that name already exists.")
            return

        attack_path = os.path.join(UPLOAD_DIR, attack_name)
        if not os.path.exists(attack_path):
            print("Couldn't process attack: '{}'".format(attack_name))
            return

        with tarfile.open(attack_path, "r") as tf:
            if is_valid_attack_tar(tf):
                attack_dir = tempfile.mkdtemp()
                extract_tar(tf, attack_dir)
                new_hash = get_hash_for_attack_dir(attack_dir)
                if new_hash not in self.attacks.values():
                    shutil.move(attack_dir, os.path.join(ATTACK_DIR, attack_name))
                    self.attacks[attack_name] = new_hash
                else:
                    print("Not processing duplicate attack: {}".format(attack_name))
            else:
                print("Invalid attack: '{}'".format(attack_name))


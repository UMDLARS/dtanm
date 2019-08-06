from web import db, redis
import tarfile
from werkzeug.datastructures import FileStorage
from flask import flash
import tempfile
import io
import hashlib
import shutil
import os
from web.models.task import add_task
from sqlalchemy.sql import func

class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255))
    hash = db.Column(db.String(255))

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team = db.relationship('Team', back_populates="attacks")

    results = db.relationship('Result', back_populates="attack", lazy="dynamic")

    created_at = db.Column(db.DateTime, server_default=func.now())

def create_attack(name: str, team_id: int, uploaded_tar: FileStorage) -> Attack:
    uploaded_tar_filename = tempfile.mktemp()
    uploaded_tar.save(uploaded_tar_filename)

    with tarfile.open(uploaded_tar_filename, "r") as tf:
        if is_valid_attack_tar(tf):
            attack_dir = tempfile.mkdtemp()
            extract_tar(tf, attack_dir)
            attack_hash = get_hash_for_attack_dir(attack_dir)

            duplicate_attacks = Attack.query.filter(Attack.hash == attack_hash)

            if duplicate_attacks.count() == 0:
                attack = Attack()
                attack.name = name
                attack.team_id = team_id
                attack.hash = attack_hash
                db.session.add(attack)
                db.session.commit()
                id = attack.id

                shutil.move(attack_dir, f'/cctf/attacks/{id}')
                shutil.move(uploaded_tar_filename, f'/cctf/attacks/{id}.tar.gz')
            else:
                dup = duplicate_attacks.first()
                os.remove(uploaded_tar_filename)
                shutil.rmtree(attack_dir)
                raise ValueError(f"Not processing duplicate attack (Duplicate of " +
                    "<a href='{ url_for('attacks.show', attack_id=dup.id) }'>dup.name</a>)")
        else:
            os.remove(uploaded_tar_filename)
            raise ValueError(f'Invalid attack submitted.')

    return attack

def is_valid_attack_tar(attack_tar: tarfile.TarFile) -> bool:
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

def extract_tar(tf, out_dir):
    # TODO: update this function to allow for directories and non_flat attacks
    for member in tf.getmembers():
        if member.isdir():
            os.makedirs(os.path.join(out_dir, member.path), exist_ok=True)
    for member in tf.getmembers():
        if member.isreg():
            with open(os.path.join(out_dir, member.path), "wb") as fp:
                fp.write(tf.extractfile(member).read())

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

def hash_stream(fp):
    BUF_SIZE = 65536
    sha = hashlib.sha512()
    while True:
        data = fp.read(BUF_SIZE)
        if not data:
            break
        sha.update(data)
    return sha.hexdigest()
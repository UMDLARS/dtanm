from web import db, redis
import tarfile
from werkzeug.datastructures import FileStorage
from flask import flash, url_for
import tempfile
import io
import hashlib
import shutil
import os
from web.models.task import add_task
from web.models.result import Result
from sqlalchemy.sql import func, text
from typing import List

class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255))
    hash = db.Column(db.String(255))

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team = db.relationship('Team', back_populates="attacks")

    created_at = db.Column(db.DateTime, server_default=func.now())

    @property
    def cmd_args(self) -> str:
        with open(f'/cctf/attacks/{self.id}/cmd_args') as f:
            return f.read()

    @property
    def stdin(self) -> str:
        with open(f'/cctf/attacks/{self.id}/stdin') as f:
            return f.read()

    @property
    def envs(self) -> str:
        with open(f'/cctf/attacks/{self.id}/env') as f:
            envs = {}
            for line in f.readlines():
                try:
                    name, value = line.split('=', 1)
                    envs[name] = value
                except:
                    pass
            return envs

    @property
    def files(self) -> List[str]:
        return os.listdir(f'/cctf/attacks/{self.id}/files')

    @property
    def results(self):
        return db.session.query(Result).from_statement(
            text("""WITH results AS (
                SELECT r.*, ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY created_at DESC) AS rn
                FROM result as r WHERE attack_id = :attack_id
                ) SELECT * from results WHERE rn = 1;
                """)
        ).params(attack_id=self.id).all()

    @property
    def passing(self):
        return db.session.query(Result).from_statement(
            text("""WITH results AS (
                SELECT r.*, ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY created_at DESC) AS rn
                FROM result as r WHERE attack_id = :attack_id
                ) SELECT * from results WHERE rn = 1 AND passed = TRUE;
                """)
        ).params(attack_id=self.id).all()

    @property
    def failing(self):
        return db.session.query(Result).from_statement(
            text("""WITH results AS (
                SELECT r.*, ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY created_at DESC) AS rn
                FROM result as r WHERE attack_id = :attack_id
                ) SELECT * from results WHERE rn = 1 AND passed = FALSE;
                """)
        ).params(attack_id=self.id).all()

    @property
    def gold_result(self) -> Result:
        return Result.query.filter(Result.attack_id == self.id).filter(Result.gold == True).order_by(Result.created_at.desc()).first()


def create_attack_from_tar(name: str, team_id: int, uploaded_tar_filename: str) -> Attack:
    with tarfile.open(uploaded_tar_filename, "r") as tf:
        attack_dir = tempfile.mkdtemp()
        if is_valid_attack_tar(tf):
            extract_tar(tf, attack_dir)
            attack = create_attack_from_directory(name, team_id, attack_dir)
            shutil.move(uploaded_tar_filename, f'/cctf/attacks/{attack.id}.tar.gz')
            return attack
        else:
            raise ValueError(f'Invalid attack submitted.')


def create_attack_from_post(name: str, team_id: int, request) -> Attack:
    """
    create_attack_from_post expects the request passed in to be validated as
    having all the necessary components (`cmd_args`, `stdin`, ...)
    """
    attack_dir = tempfile.mkdtemp()
    with open(os.path.join(attack_dir, "cmd_args"), 'w+') as f:
        f.write(request.form.get('cmd_args'))
    with open(os.path.join(attack_dir, "stdin"), 'w+') as f:
        f.write(request.form.get('stdin'))
    with open(os.path.join(attack_dir, "env"), 'w+') as f:
        f.write(request.form.get('env'))
    os.mkdir(os.path.join(attack_dir, "files"))
    # for file in request.files.env: # save in env

    _, tar_path = tempfile.mkstemp()
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(attack_dir, arcname=os.path.basename(attack_dir))

        attack = create_attack_from_directory(name, team_id, attack_dir)
        shutil.move(tar_path, f'/cctf/attacks/{attack.id}.tar.gz')
        return attack

def create_attack_from_directory(name: str, team_id: int, directory: str) -> Attack:
    attack_hash = get_hash_for_attack_dir(directory)
    duplicate_attacks = Attack.query.filter(Attack.hash == attack_hash)
    if duplicate_attacks.count() == 0:
        attack = Attack()
        attack.name = name
        attack.team_id = team_id
        attack.hash = attack_hash
        db.session.add(attack)
        db.session.commit()
        id = attack.id

        shutil.move(directory, f'/cctf/attacks/{id}')
        return attack
    else:
        dup = duplicate_attacks.first()
        raise ValueError("Not processing duplicate attack (Duplicate of " +
            f"<a href='{ url_for('attacks.show', attack_id=dup.id) }'>{dup.name}</a>)")

def is_valid_attack_tar(attack_tar: tarfile.TarFile) -> bool:
    has_cmd_args = has_stdin = has_env = has_files = False
    for member in attack_tar.getmembers():
        if member.path[0] == '/':
            return False
        elif '..' in member.path:
            return False
        if member.path == "cmd_args" and member.isreg():
            has_cmd_args = True
        if member.path == "stdin" and member.isreg():
            has_stdin = True
        if member.path == "env" and member.isreg():
            has_env = True
        if member.path == "files" and member.isdir():
            has_files = True
    return has_cmd_args and has_stdin and has_env and has_files

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

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
from sqlalchemy.sql import func, text
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy import select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, aliased
from datetime import datetime

from web import app

if TYPE_CHECKING:
    from web.models.team import Team
    from web.models.result import Result

class Attack(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255))
    hash: Mapped[str] = mapped_column(String(255))

    team_id: Mapped[int] = mapped_column(ForeignKey('team.id'))
    team: Mapped[Optional["Team"]] = relationship(back_populates="attacks")

    results: Mapped[List['Result']] = relationship(back_populates="attack", cascade="all, delete")

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

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

    # This massive expression is needed because the db holds all results 
    # for all past tests; results are never deleted.
    # This grabs the latest results against this attack for each team.
    def _get_results(self, passing):
        from web.models.result import Result

        by_created_time = (
            select(
                Result,
                func.row_number()
                    .over(partition_by=Result.team_id, order_by=Result.created_at.desc())
                    .label("rn")
            )
            .where(Result.attack_id == self.id)
            .cte()
        )
        stmt = (
            select(aliased(Result, by_created_time))
            .where(by_created_time.c.rn == 1)
            .where(by_created_time.c.passing == passing)
        )

        return db.session.scalars(stmt).all()

    @property
    def passing(self):
        from web.models.result import Result
        return self._get_results(True)

    @property
    def failing(self):
        from web.models.result import Result
        return self._get_results(False)

    @property
    def curent_results(self):
        from web.models.result import Result

        by_created_time = (
            select(
                Result,
                func.row_number()
                    .over(partition_by=Result.team_id, order_by=Result.created_at.desc())
                    .label("rn")
            )
            .where(Result.attack_id == self.id)
            .cte()
        )
        stmt = (
            select(aliased(Result, by_created_time))
            .where(by_created_time.c.rn == 1)
        )

        return db.session.scalars(stmt).all()

    @property
    def gold_result(self) -> Result:
        from web.models.result import Result
        stmt = (
            select(Result)
            .where(Result.attack_id == self.id)
            .where(Result.gold == True)
            .order_by(Result.created_at.desc())
        )
        return db.session.scalars(stmt).first()


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

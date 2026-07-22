import os
import shutil
import dulwich.porcelain as git
from dulwich.repo import Repo

bare_repo = None
repo = None

def copy_external_pack(path: str):
    global bare_repo, repo
    shutil.rmtree('/cctf/pack_bare', ignore_errors=True)
    shutil.rmtree('/cctf/pack', ignore_errors=True)
    os.mkdir('/cctf/pack_bare')
    bare_repo = Repo.init_bare('/cctf/pack_bare')
    repo = git.clone('/cctf/pack_bare', '/cctf/pack')
    shutil.copytree(path, '/cctf/pack', dirs_exist_ok=True, ignore=lambda d,l: ['.git'] if '.git' in l else [])
    git.add(repo=repo)
    author=f"DTANM Admin <admin@lars.d.umn.edu>" # TODO: better email?
    git.commit(repo=repo, message="Initial Commit", author=author)
    git.push(repo=repo)

def init_pack():
    if not os.path.isdir('/cctf/pack_bare'):
        copy_external_pack('/pack_external')

def update_pack_clone():
    git.pull(repo=repo)

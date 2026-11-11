import os
import shutil
import dulwich.porcelain as git
from dulwich.repo import Repo
from packaging.version import Version

MIN_SUPPORTED_PACK_VER = Version("4.0")
MAX_SUPPORTED_PACK_VER = Version("4.0")

pack_version = None
enable_inst_formatting = True

bare_repo = None
checked_repo = None

# NOTE: Updating the config requires a restart

def copy_external_pack(path: str):
    global bare_repo, checked_repo

    # Remove any old repo data.
    shutil.rmtree('/cctf/pack_bare', ignore_errors=True)
    shutil.rmtree('/cctf/pack', ignore_errors=True)

    # Create the bare repo.
    os.mkdir('/cctf/pack_bare')
    bare_repo = Repo.init_bare('/cctf/pack_bare')

    # Clone the repo and copy the pack contents over.
    checked_repo = git.clone('/cctf/pack_bare', '/cctf/pack')
    shutil.copytree(path, '/cctf/pack', dirs_exist_ok=True, ignore=lambda d,l: ['.git'] if '.git' in l else [])

    # Commit and push the additions.
    git.add(repo=checked_repo)
    author=f"DTANM Admin <admin@lars.d.umn.edu>" # TODO: better email?
    git.commit(repo=checked_repo, message="Initial Commit", author=author)
    git.push(repo=checked_repo)

def init_pack():
    if not os.path.isdir('/cctf/pack_bare'):
        copy_external_pack('/pack_external')

def update_pack_clone():
    git.pull(repo=checked_repo)

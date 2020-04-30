from flask import render_template, Blueprint, make_response, request, abort, flash, redirect
from flask_security import login_required, current_user, http_auth_required, roles_required
from web import db, redis, team_required
from web.models.team import Team
from dulwich.repo import Repo

program = Blueprint('program', __name__, template_folder='templates')

@program.route('/')
@login_required
@team_required
def index():
    try:
        r = Repo(os.path.join('/cctf/repos/', str(current_user.team_id)))
        commit = r.get_object(r.head())
    except KeyError:
        flash("No commits have been submitted yet.", category="info")
        commit=None
    git_url=f"{request.url_root}program"
    return render_template('program/submit.html', commit=commit, git_url=git_url)

@program.route('/<int:team_id>')
@login_required
@roles_required('admin')
def index_team(team_id: int):
    try:
        r = Repo(os.path.join('/cctf/repos/', str(team_id)))
        commit = r.get_object(r.head())
    except KeyError:
        flash("No commits have been submitted yet.", category="info")
        commit=None
    git_url=f"{request.url_root}program/{team_id}"
    return render_template('program/submit.html', commit=commit, git_url=git_url)

@program.route('/', methods=['POST'])
@login_required
@team_required
def store():
    # check if the post request has the file part
    if 'program' not in request.files:
        flash('No file attribute in request', category="error")
        return redirect(request.referrer)

    program = request.files['program']
    # if user does not select file, browser also
    # submit an empty part without filename
    if not program or program.filename == '':
        flash('No file uploaded', category="error")
        return redirect(request.referrer)

    try:
        raise NotImplementedError("Tarball extraction is not yet supported")
        flash(
            f"You've updated your program.",
            category="success"
        )
    except Exception as e:
        flash(str(e), category="error")

    return redirect(request.referrer)


## EXPOSE TEAM GIT ENDPOINTS

@program.route('/info/refs')
@http_auth_required
def info_refs_user():
    return info_refs(current_user.team_id)

@program.route('/git-receive-pack', methods=('POST',))
@http_auth_required
def git_receive_pack_user():
    return git_receive_pack(current_user.team_id)


@program.route('/git-upload-pack', methods=('POST',))
@http_auth_required
def git_upload_pack_user():
    return git_upload_pack(current_user.team_id)


## EXPOSE ADMIN GIT ENDPOINTS

@program.route('/<int:team_id>/info/refs')
@http_auth_required
@roles_required('admin')
def info_refs_admin(team_id: int):
    return info_refs(team_id)

@program.route('/<int:team_id>/git-receive-pack', methods=('POST',))
@http_auth_required
@roles_required('admin')
def git_receive_pack_admin(team_id: int):
    return git_receive_pack(team_id)

@program.route('/<int:team_id>/git-upload-pack', methods=('POST',))
@http_auth_required
@roles_required('admin')
def git_upload_pack_admin(team_id: int):
    return git_upload_pack(team_id)


####
## Git endpoints follow:
####

from flask import Flask, make_response, request, abort
from io import BytesIO
from dulwich.pack import PackStreamReader
import subprocess, os.path

def info_refs(team_id: int):
    service = request.args.get('service')
    if service[:4] != 'git-':
        abort(500)
    p = subprocess.Popen([service, '--stateless-rpc', '--advertise-refs', os.path.join('/cctf/repos/', str(team_id))], stdout=subprocess.PIPE)
    packet = '# service=%s\n' % service
    length = len(packet) + 4
    _hex = '0123456789abcdef'
    prefix = ''
    prefix += _hex[length >> 12 & 0xf]
    prefix += _hex[length >> 8  & 0xf]
    prefix += _hex[length >> 4 & 0xf]
    prefix += _hex[length & 0xf]
    data = prefix + packet + '0000'
    data += p.stdout.read().decode('utf-8')
    res = make_response(data)
    res.headers['Expires'] = 'Fri, 01 Jan 1980 00:00:00 GMT'
    res.headers['Pragma'] = 'no-cache'
    res.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate'
    res.headers['Content-Type'] = 'application/x-%s-advertisement' % service
    p.wait()
    return res

def git_receive_pack(team_id: int):
    p = subprocess.Popen(['git-receive-pack', '--stateless-rpc', os.path.join('/cctf/repos/', str(team_id))], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    data_in = request.data
    pack_file = data_in[data_in.index(b'PACK'):]
    objects = PackStreamReader(BytesIO(pack_file).read)
    repo_updated = False
    for obj in objects.read_objects():
        if obj.obj_type_num == 1: # Commit
            repo_updated = True
    if repo_updated:
        Team.query.get(team_id).rescore_all_attacks()
    p.stdin.write(data_in)
    p.stdin.close()
    data_out = p.stdout.read()
    res = make_response(data_out)
    res.headers['Expires'] = 'Fri, 01 Jan 1980 00:00:00 GMT'
    res.headers['Pragma'] = 'no-cache'
    res.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate'
    res.headers['Content-Type'] = 'application/x-git-receive-pack-result'
    p.wait()
    return res

def git_upload_pack(team_id: int):
    p = subprocess.Popen(['git-upload-pack', '--stateless-rpc', os.path.join('/cctf/repos/', str(team_id))], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(request.data)
    p.stdin.close()
    data = p.stdout.read()
    res = make_response(data)
    res.headers['Expires'] = 'Fri, 01 Jan 1980 00:00:00 GMT'
    res.headers['Pragma'] = 'no-cache'
    res.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate'
    res.headers['Content-Type'] = 'application/x-git-upload-pack-result'
    p.wait()
    return res

from flask import render_template, Blueprint, make_response, request, abort, flash, redirect
from flask_security import login_required, current_user, http_auth_required
from web import db, redis
from web.models.team import Team
from dulwich.repo import Repo
from web.models.task import add_task
from web.models.attack import Attack

program = Blueprint('program', __name__, template_folder='templates')

@program.route('/')
@login_required
def index():
    try:
        commit=Repo(os.path.join('/cctf/repos/', str(current_user.team_id))).head()
    except KeyError:
        flash("No commits have been submitted yet.", category="info")
        commit=None
    return render_template('program/submit.html', commit=commit)

@program.route('/', methods=['POST'])
@login_required
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

####
## Git endpoints follow:
####

from flask import Flask, make_response, request, abort
from io import BytesIO
from dulwich.pack import PackStreamReader
import subprocess, os.path

@program.route('/info/refs')
@http_auth_required
def info_refs():
    service = request.args.get('service')
    if service[:4] != 'git-':
        abort(500)
    p = subprocess.Popen([service, '--stateless-rpc', '--advertise-refs', os.path.join('/cctf/repos/', str(current_user.team_id))], stdout=subprocess.PIPE)
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

@program.route('/git-receive-pack', methods=('POST',))
@http_auth_required
def git_receive_pack():
    p = subprocess.Popen(['git-receive-pack', '--stateless-rpc', os.path.join('/cctf/repos/', str(current_user.team_id))], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    data_in = request.data
    pack_file = data_in[data_in.index(b'PACK'):]
    objects = PackStreamReader(BytesIO(pack_file).read)
    repo_updated = False
    for obj in objects.read_objects():
        if obj.obj_type_num == 1: # Commit
            repo_updated = True
    if repo_updated:
        for attack in Attack.query.all():
            add_task(current_user.team_id, attack.id)
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

@program.route('/git-upload-pack', methods=('POST',))
@http_auth_required
def git_upload_pack():
    p = subprocess.Popen(['git-upload-pack', '--stateless-rpc', os.path.join('/cctf/repos/', str(current_user.team_id))], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
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

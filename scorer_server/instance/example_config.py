""" This is an example Config file.
    To use this file copy it to `config.py`
"""

PORT = 2000

TASKER_LOOP_TIMEOUT_SEC = 0.25
WORKER_COUNT = 1

UPLOAD_DIR = "/cctf/server/uploads"
ATTACKS_DIR = "/cctf/attacks/"
TEAM_DIR = "/cctf/server/gitrepos"

RESULT_SUBMIT_URL = "http://localhost:5000/results"

SCORING_BIN_NAME = "prog"
SCORING_GOLD_NAME = "gold"
SCORING_GOLD_SRC = "/home/derpferd/src/dtanm/root/gold"

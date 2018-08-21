""" This is an example Config file.
    To use this file copy it to `config.py`
"""

PORT = 2000

TASKER_LOOP_TIMEOUT_SEC = 0.25
WORKER_COUNT = 1

UPLOAD_DIR = "/Users/beauliej/p/src/mock_root/cctf/server/uploads"
ATTACKS_DIR = "/Users/beauliej/p/src/mock_root/cctf/attacks/"
TEAM_DIR = "/Users/beauliej/p/src/mock_root/cctf/server/gitrepos"
RESULTS_DIR = "/Users/beauliej/p/src/mock_root/ccft/results"

RESULT_SUBMIT_URL = "http://localhost:5000/results"

SCORING_BIN_NAME = "prog"
SCORING_GOLD_NAME = "gold"
SCORING_GOLD_SRC = "/Users/beauliej/p/src/mock_root/cctf/gold"

START_TASKER = True

import datetime as dt

import json
import time

save = None

def register_save_object(s):
    global save
    save: None = s

def get_save():
    return save

# This is for persistent that would be weird to use the db for.
class SaveData:
    def __init__(self, save_path, conf):
        self.save_path = save_path

        # Read and parse the save file.
        try:
            with open(save_path) as fp:
                parsed = json.load(fp)
        except OSError as e:
            # Setup defaults.
            self.started_time         = time.time()

            # Convert attack diff to seconds if needed.
            attack_diff = conf['ATTACK_DEADLINE']
            if isinstance(attack_diff, dt.timedelta):
                attack_diff = attack_diff.seconds

            # Same for competition diff.
            comp_diff = conf['COMPETITION_DEADLINE']
            if isinstance(comp_diff, dt.timedelta):
                comp_diff = comp_diff.seconds

            # Compute actual deadlines.
            self.attack_deadline      = self.started_time + attack_diff
            self.competition_deadline = self.started_time + comp_diff

            # Save edits.
            self.write()
            return

        # Grab relevant fields.
        self.started_time         = parsed['started_time']
        self.attack_deadline      = parsed['attack_deadline']
        self.competition_deadline = parsed['competition_deadline']

    def write(self):
        # Setup json fields.
        fields = {
            'started_time':         self.started_time,
            'attack_deadline':      self.attack_deadline,
            'competition_deadline': self.competition_deadline,
        }

        # Encode and write them out.
        with open(self.save_path, 'w') as fp:
            json.dump(fields, fp)

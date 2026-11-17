import datetime as dt

import json
import time

_save_obj = None

def register_save_object(save):
    _save_obj = save

def get_save():
    return _save_obj

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
            self.attack_end_time      = self.started_time + conf['ATTACK_DEADLINE']
            self.competition_end_time = self.started_time + conf['COMPETITION_DEADLINE']
            self.commit()
            return

        # Grab relevant fields.
        self.started_time         = parsed['started_time']
        self.attack_end_time      = parsed['attack_end_time']
        self.competition_end_time = parsed['competition_end_time']

    def commit(self):
        # Setup json fields.
        fields = {
            'started_time':         self.started_time,
            'attack_end_time':      self.attack_end_time,
            'competition_end_time': self.competition_end_time,
        }

        # Encode and write them out.
        with open(self.save_path, 'w') as fp:
            json.dump(fields, fp)

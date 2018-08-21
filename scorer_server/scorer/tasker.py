import logging
from multiprocessing import Process
from typing import Optional

from scorer.db.update import next_update
from scorer.db.task import add_task


class Tasker(Process):
    def __init__(self):
        self.attacks = set()
        self.teams = set()
        self.log = logging.getLogger(__name__)
        super().__init__()

    def _process_update(self, update: Optional[str]):
        if update is None:
            return

        if update.count('-') != 1:
            self.log.warning(f"Invalid update: '{update}'")
            return
        update_type, update_id = update.split('-')

        if update_type == 't':
            self.log.info(f'Got update. Team: {update_id}')
            self.teams.add(update_id)
            for attack in self.attacks:
                add_task(update_id, attack)
        elif update_type == 'a':
            self.log.info(f'Got update. Attack: {update_id}')
            self.attacks.add(update_id)
            for team in self.teams:
                add_task(team, update_id)
        else:
            self.log.info(f"Invalid update type. Update: '{update}'")

    def run(self):
        try:
            while True:
                update = next_update()
                self._process_update(update)
        except KeyboardInterrupt:
            pass


import logging
from time import sleep
from multiprocessing import Process
from scorer.db.update import next_update
from scorer.db.task import add_task


class Tasker(Process):
    def __init__(self):
        self.attacks = set()
        self.teams = set()
        self.log = logging.getLogger(__name__)
        super().__init__()

    def run(self):
        try:
            while True:
                try:
                    update = next_update()
                    self.log.info(f'Got update: {update}')
                    update_type, update_id = update.split('-')
                except Exception as e:
                    self.log.info(f'Invalid update:\n {e}')
                    continue
                if update_type == 't':
                    self.teams.add(update_id)
                    for attack in self.attacks:
                        add_task(update_id, attack)
                elif update_type == 'a':
                    self.attacks.add(update_id)
                    for team in self.teams:
                        add_task(team, update_id)
                else:
                    self.log.info('Invalid update type')
        except KeyboardInterrupt:
            pass


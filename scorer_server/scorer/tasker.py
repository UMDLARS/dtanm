import queue
import time
from collections import deque
from logging import Logger
from multiprocessing import Process, Queue, Event
from typing import Set

from flask import current_app

from scorer.attack import Attack
from scorer.manager import AttackManager, TeamManager
from scorer.tasks import AttackUpdate, TeamUpdate, ScoreTask
from scorer.team import Team
from scorer.worker import Scorer, ScoringConfig


class SingletonDecorator:
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


@SingletonDecorator
class TaskerStore:
    def __init__(self):
        self.attack_manager = None
        self.team_manager = None
        self.task_queue = None
        self.tasker = None


def get_team_manager():
    store = TaskerStore()
    if store.team_manager is None:
        store.team_manager = TeamManager(team_dir=current_app.config["TEAM_DIR"])

    return store.team_manager


def get_attack_manager():
    store = TaskerStore()
    if store.attack_manager is None:
        store.attack_manager = AttackManager(upload_dir=current_app.config["UPLOAD_DIR"],
                                             attacks_dir=current_app.config["ATTACKS_DIR"])

    return store.attack_manager


def get_task_queue():
    store = TaskerStore()
    if store.task_queue is None:
        store.task_queue = Queue()

    return store.task_queue


def get_tasker():
    store = TaskerStore()
    if store.tasker is None:
        current_app.logger.info("Creating Tasker...")
        store.tasker = Tasker(queue=get_task_queue(),
                              attacks=get_attack_manager().load_existing_attacks())

    return store.tasker


def start_tasker():
    get_tasker().start()


def stop_tasker(e=None):
    tasker = TaskerStore().tasker
    if tasker:
        tasker.shutdown_flag.set()
        tasker.join()


def init_app():
    current_app.logger.info(f"Setting up tasker...")
    start_tasker()


class Tasker(Process):
    teams: Set[Team]
    attacks: Set[Attack]
    shutdown_flag: Event  # If this is set: the Process will shutdown nicely.

    logger: Logger

    def __init__(self, queue: Queue, attacks=None):
        self.timeout = current_app.config["TASKER_LOOP_TIMEOUT_SEC"]
        self.worker_count = current_app.config["WORKER_COUNT"]  # number of processing to use to score.

        if attacks is None:
            self.attacks = set()
        else:
            self.attacks = set(attacks)

        self.in_queue = queue
        self.out_queue = Queue(self.worker_count)
        self.tasks = deque()  # a buffer of pending tasks for when the out_queue is full.
        self.teams = set()
        self.scorers = set()

        self.shutdown_flag = Event()
        self.logger = current_app.logger

        super().__init__()

    def start_scorers(self):
        self.scorers = set()
        # setup and start scorer process pool.
        for _ in range(self.worker_count):
            scorer_config = ScoringConfig(current_app.config["SCORING_BIN_NAME"],
                                          current_app.config["SCORING_GOLD_NAME"],
                                          current_app.config["SCORING_GOLD_SRC"],
                                          current_app.config['RESULTS_DIR'])
            worker = Scorer(self.out_queue, scorer_config)
            worker.start()
            self.scorers.add(worker)

    def process_in_queue(self):
        """

        Returns: True if a task was processed.
        """
        try:
            task = self.in_queue.get(block=False, timeout=.01)
            current_app.logger.debug(f"Tasker got task: {task}")
            if task is None:
                raise InterruptedError
            if isinstance(task, AttackUpdate):
                attack = task.data
                if attack not in self.attacks:
                    self.attacks.add(attack)
                for team in self.teams:
                    task = ScoreTask(team=team, attack=attack)
                    if task not in self.tasks:
                        self.tasks.append(task)
            elif isinstance(task, TeamUpdate):
                team = task.data
                if team not in self.teams:
                    self.teams.add(team)
                for attack in self.attacks:
                    task = ScoreTask(team=team, attack=attack)
                    if task not in self.tasks:
                        self.tasks.append(task)
            return True
        except queue.Empty:
            return False

    def update_out_queue(self):
        """

        Returns: True if a task was processed.
        """
        task_processed = False
        while self.worker_count - self.out_queue.qsize() and len(self.tasks):
            task = self.tasks.popleft()
            self.logger.debug("Tasker: adding {} to scoring queue...".format(task))
            self.out_queue.put(task)
            task_processed = True
        return task_processed

    def run(self):
        self.logger.info("Starting Tasker...")
        self.start_scorers()
        try:
            while not self.shutdown_flag.is_set():
                sleep_needed = True

                # Get a task and update the task set.
                # If we got one we need not sleep.
                if self.process_in_queue():
                    sleep_needed = False

                # Update task queue from task set.
                # If we got one we need not sleep.
                if self.update_out_queue():
                    sleep_needed = False

                if sleep_needed:
                    time.sleep(self.timeout)
        except InterruptedError:
            pass
        except KeyboardInterrupt:
            pass

        self.logger.info("Tasker Process shutting down...")

        # Shutdown workers.
        for _ in range(self.worker_count):
            if not self.out_queue.full():
                self.out_queue.put_nowait(None)

        self.logger.info("Tasker Process waiting for Workers...")
        for scorer in self.scorers:
            scorer.join()

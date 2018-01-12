# Under MIT License, see LICENSE.txt
__author__ = "Maxime Gagnon-Legault"

import logging
from multiprocessing import Event, Queue
import signal  # so we can stop gracefully
import time

from RULEngine.engine import Engine
from ai.coach import Coach
from config.config_service import ConfigService


class Framework(object):
    """
        La classe contient la logique nécessaire pour communiquer avec
        les différentes parties(simulation, vision, uidebug et/ou autres),
         maintenir l'état du monde (jeu, referree, debug, etc...) et appeller
         l'ia.
    """

    def __init__(self):
        """ Constructeur de la classe, établis les propriétés de bases et
        construit les objets qui sont toujours necéssaire à son fonctionnement
        correct.
        """

        # logger
        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger("Framework")
        # config
        self.cfg = ConfigService()

        # Events
        self.ai_terminating_event = Event()
        self.engine_terminating_event = Event()

        # Queues
        self.game_state_queue = Queue()
        self.ai_queue = Queue()
        self.ui_send_queue = Queue()
        self.ui_recv_queue = Queue()

        # Engine
        self.engine = Engine(self.game_state_queue, self.ai_queue, self.ui_send_queue, self.ui_recv_queue, self.engine_terminating_event)
        self.engine.start()

        # AI
        self.coach = Coach(self.game_state_queue, self.ai_queue, self.ui_send_queue, self.ui_recv_queue, self.ai_terminating_event)
        self.coach.start()

        # end signal - do you like to stop gracefully? DO NOT MOVE! MUST BE PLACED AFTER PROCESSES
        signal.signal(signal.SIGINT, self._sigint_handler)

        # stop until someone manually stop us / we receive interrupt signal from os
        signal.pause()

    def stop_game(self):
        self.logger.info('STOP GAME')

        self.engine_terminating_event.set()
        self.engine.terminate()

        self.ai_terminating_event.set()
        self.coach.join(1)

        exit(0)

    # noinspection PyUnusedLocal
    def _sigint_handler(self, *args):
        self.stop_game()

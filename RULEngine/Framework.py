# Under MIT License, see LICENSE.txt

import logging
from multiprocessing import Event, Queue
import signal  # so we can stop gracefully

from RULEngine.engine import Engine
from ai.coach import Coach
from config.config_service import ConfigService

__author__ = "Maxime Gagnon-Legault"


class Framework:
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

        # Queues
        self.game_state_queue = Queue()
        self.ai_queue = Queue()
        self.ui_send_queue = Queue()
        self.ui_recv_queue = Queue()

        # Engine
        self.engine = Engine(self.game_state_queue,
                             self.ai_queue,
                             self.ui_send_queue,
                             self.ui_recv_queue)
        self.engine.start()

        # AI
        self.coach = Coach(self.game_state_queue,
                           self.ai_queue,
                           self.ui_send_queue,
                           self.ui_recv_queue)
        self.coach.start()

        # end signal - do you like to stop gracefully? DO NOT MOVE! MUST BE PLACED AFTER PROCESSES
        signal.signal(signal.SIGINT, self._sigint_handler)

        # stop until someone manually stop us / we receive interrupt signal from os
        signal.pause()

    def stop_game(self):
        self.engine.terminate()
        self.coach.terminate()

        exit(0)

    # noinspection PyUnusedLocal
    # pylint: disable=unused-argument
    def _sigint_handler(self, *args):
        self.logger.info("*************************")
        self.logger.info("Received interrupt signal from the os. Starting shutdown sequence")
        self.stop_game()

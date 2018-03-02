# Under MIT license, see LICENSE.txt
import time

from Util import Pose, AICommand
from ai.GameDomainObjects import Player
from ai.STA.Action import Action
from ai.states import GameState
COMMAND_DELAY = 0.5

class KickCharge(Action):

    def __init__(self, game_state: GameState, player: Player, kick_type=1):
        Action.__init__(self, game_state, player)

        self.kick_type = kick_type
        self.player = player

    def exec(self):


        # todo charge kick here please/ask Simon what kicktype is supposed to be
        return AICommand(self.player.id, kick_type=self.kick_type)
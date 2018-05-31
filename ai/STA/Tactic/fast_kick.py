from typing import List

from Util import Pose
from Util.ai_command import CmdBuilder
from Util.constant import KickForce
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


GRAB_BALL_SPACING = 100
KICK_DISTANCE = 130

class FastKick(Tactic):

    def __init__(self, game_state: GameState, player: Player,
                 target: Pose=Pose(),
                 args: List[str]=None,
                 kick_force: KickForce=KickForce.MEDIUM):

        super().__init__(game_state, player, target, args)
        self.current_state = self.kick_charge
        self.next_state = self.kick_charge

    def kick_charge(self):
        self.next_state = self.grab_ball()
        return CmdBuilder().addChargeKicker().build()

    def grab_ball(self):
        if (self.player.position - self.game_state.ball_position).norm <= KICK_DISTANCE:
            self.next_state = self.kick()

        orientation = (self.target.position - self.game_state.ball_position).angle
        dest_position = self.game_state.ball_position
        return CmdBuilder().addMoveTo(Pose(dest_position, orientation),
                                      cruise_speed=1,
                                      ball_collision=False).addForceDribbler().addChargeKicker().build()

    def kick(self):
        return
        # self.ball_spacing = GRAB_BALL_SPACING
        # self.next_state = self.validate_kick
        # self.tries_flag += 1
        #
        # player_to_target = (self.target.position - self.player.pose.position)
        # behind_ball = self.game_state.ball_position - normalize(player_to_target) * (BALL_RADIUS + ROBOT_CENTER_TO_KICKER)
        # orientation = player_to_target.angle
        #
        # return CmdBuilder().addMoveTo(Pose(behind_ball, orientation)).addKick(self.kick_force).build()
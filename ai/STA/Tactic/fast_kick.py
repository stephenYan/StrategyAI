from typing import List

from Util import Pose, Position
from Util.ai_command import CmdBuilder, Idle
from Util.constant import KickForce
from Util.geometry import compare_angle
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


GRAB_BALL_SPACING = 100
KICK_DISTANCE = 130
KICK_SUCCEED_THRESHOLD = 600
VALID_DIFF_ANGLE = 0.2


class FastKick(Tactic):

    def __init__(self, game_state: GameState, player: Player,
                 target: Pose=Pose(),
                 args: List[str]=None,
                 kick_force: KickForce=KickForce.MEDIUM,
                 move_speed=0.5):

        super().__init__(game_state, player, target, args)
        self.current_state = self.kick_charge
        self.next_state = self.kick_charge
        self.kick_force = kick_force
        self.move_speed = move_speed
        self.target_orientation = (self.target.position - self.game_state.ball_position).angle

    def kick_charge(self):
        if self._verify_position():
            self.next_state = self.grab_ball
        else:
            self.next_state = self.reposition
        return CmdBuilder().addChargeKicker().build()

    def reposition(self):
        if self._verify_position():
            self.next_state = self.grab_ball
        return CmdBuilder().addMoveTo(self._get_valid_pose(),
                                      cruise_speed=2,
                                      end_speed=0).addChargeKicker().build()

    def grab_ball(self):
        if (self.player.position - self.game_state.ball_position).norm <= KICK_DISTANCE:
            self.next_state = self.kick

        orientation = self.target_orientation
        dest_position = self.game_state.ball_position
        return CmdBuilder().addMoveTo(Pose(dest_position, orientation),
                                      cruise_speed=self.move_speed,
                                      ball_collision=False).addForceDribbler().addChargeKicker().build()

    def kick(self):
        self.next_state = self.validate_kick

        orientation = self.target_orientation
        dest_position = self.game_state.ball_position
        return CmdBuilder().addMoveTo(Pose(dest_position, orientation),
                                      cruise_speed=self.move_speed,
                                      ball_collision=False).addKick(self.kick_force).build()

    def validate_kick(self):
        if self.game_state.ball_velocity.norm > 1000 or \
                (self.player.pose.position - self.game_state.ball_position).norm > KICK_SUCCEED_THRESHOLD:
            self.next_state = self.halt
        else:
            self.next_state = self.grab_ball

        return CmdBuilder().build()

    def halt(self):
        return Idle

    def _get_alignment(self):
        return (self.game_state.ball_position - self.player.position).angle

    def _verify_position(self):
        return compare_angle(self.target_orientation, self._get_alignment(), VALID_DIFF_ANGLE) and \
                compare_angle(self.target_orientation, self.player.pose.orientation, VALID_DIFF_ANGLE)

    def _get_valid_pose(self):
        target_position = self.game_state.ball_position - Position.from_angle(self.target_orientation,
                                                                              norm=GRAB_BALL_SPACING*3)
        return Pose(target_position, self.target_orientation)

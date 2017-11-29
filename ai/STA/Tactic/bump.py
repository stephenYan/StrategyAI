# Under MIT licence, see LICENCE.txt
import math
from typing import List

import numpy as np
import time

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.GameDomainObjects.player import Player
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import ROBOT_RADIUS
from RULEngine.Util.geometry import get_distance
from ai.STA.Action.AllStar import AllStar
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.GoBehind import GoBehind
from ai.Util.ai_command import AICommandType
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'


class Bump(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.current_state = self.get_behind_ball
        self.next_state = self.get_behind_ball
        self.debug_interface = DebugInterface()
        self.move_action = self._generate_move_to()
        self.move_action.status_flag = Flags.SUCCESS
        self.last_ball_position = self.game_state.get_ball_position()
        self.charge_time = 0
        self.last_time = time.time()

        self.orientation_target = 0
        self.target = target

    def get_behind_ball(self):
        self.status_flag = Flags.WIP

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y

        vector_player_2_ball = np.array([ball_x - player_x, ball_y - player_y])
        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)

        if self._is_player_opposing_ball_and_target():
            self.next_state = self.push_ball
            self.last_ball_position = self.game_state.get_ball_position()
        else:
            # self.debug.add_log(4, "Distance from ball: {}".format(dist))
            self.next_state = self.get_behind_ball
        return GoBehind(self.game_state, self.player, self.game_state.get_ball_position(), self.target.position,
                        120, pathfinder_on=True, orientation='back')

    def push_ball(self):
        # self.debug.add_log(1, "Grab ball called")
        # self.debug.add_log(1, "vector player 2 ball : {} mm".format(self.vector_norm))
        if get_distance(self.last_ball_position, self.player.pose.position) < 40:
            self.next_state = self.halt
            self.last_time = time.time()
        elif self._is_player_opposing_ball_and_target(-0.9):
            self.next_state = self.push_ball
        else:
            self.next_state = self.get_behind_ball
        # self.debug.add_log(1, "orientation go get ball {}".format(self.last_angle))
        target = self.target.position.conv_2_np()
        player = self.player.pose.position.conv_2_np()
        player_to_target = target - player
        player_to_target = 0.5 * player_to_target / np.linalg.norm(player_to_target)
        speed_pose = Pose(Position.from_np(player_to_target))
        return Move(self.game_state, self.player, speed_pose)

    def halt(self):
        self.next_state = self.halt
        self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)

    def _get_distance_from_ball(self):
        return get_distance(self.player.pose.position,
                            self.game_state.get_ball_position())

    def _is_player_opposing_ball_and_target(self, fact=-0.99):

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y

        target_x = self.target.position.x
        target_y = self.target.position.y

        vector_player_2_ball = np.array([ball_x - player_x, ball_y - player_y])
        vector_target_2_ball = np.array([ball_x - target_x, ball_y - target_y])
        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)
        vector_target_2_ball /= np.linalg.norm(vector_target_2_ball)
        vector_player_dir = np.array([np.cos(self.player.pose.orientation),
                                      np.sin(self.player.pose.orientation)])
        if np.dot(vector_player_2_ball, vector_target_2_ball) < fact:
            if not (np.dot(vector_player_dir, vector_target_2_ball) < fact):
                return True
        return False

    def _generate_move_to(self):
        player_pose = self.player.pose
        ball_position = self.game_state.get_ball_position()

        dest_position = self.get_behind_ball_position(ball_position)
        destination_pose = Pose(dest_position, player_pose.orientation)

        return AllStar(self.game_state, self.player, **{"pose_goal": destination_pose,
                                                        "ai_command_type": AICommandType.MOVE})

    def get_behind_ball_position(self, ball_position):
        vec_dir = self.target.position - ball_position
        mag = math.sqrt(vec_dir.x ** 2 + vec_dir.y ** 2)
        scale_coeff = ROBOT_RADIUS * 3 / mag
        dest_position = ball_position - (vec_dir * scale_coeff)
        return dest_position

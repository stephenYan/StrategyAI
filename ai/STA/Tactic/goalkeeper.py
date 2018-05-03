# Under MIT licence, see LICENCE.txt
from unittest.suite import _DebugResult

import numpy as np

from Debug.debug_command_factory import DebugCommandFactory

__author__ = 'RoboCupULaval'

import time
from math import tan, pi
from typing import List

from Util import Pose, Position, AICommand
from Util.ai_command import CmdBuilder, MoveTo
from Util.constant import ROBOT_RADIUS, KickForce
from Util.constant import TeamColor
from Util.geometry import clamp, compare_angle, wrap_to_pi, intersection_line_and_circle
from ai.Algorithm.evaluation_module import closest_player_to_point, best_passing_option, player_with_ball
from ai.GameDomainObjects.field import FieldSide
from ai.GameDomainObjects import Player

from ai.STA.Action.ProtectGoal import ProtectGoal
from ai.STA.Tactic.go_kick import GRAB_BALL_SPACING, KICK_DISTANCE, VALIDATE_KICK_DELAY, KICK_SUCCEED_THRESHOLD

from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

TARGET_ASSIGNATION_DELAY = 1


class GoalKeeper(Tactic):
    """
    Tactique du gardien de but standard. Le gardien doit se placer entre la balle et le but, tout en restant à
    l'intérieur de son demi-cercle. Si la balle entre dans son demi-cercle, le gardien tente d'aller en prendre
    possession.
    """

    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(),
                 penalty_kick=False, args: List[str]=None,):
        super().__init__(game_state, player, target, args)

        self.is_yellow = self.player.team.team_color == TeamColor.YELLOW
        self.current_state = self.defense
        self.next_state = self.defense
        # self.current_state = self.protect_goal
        # self.next_state = self.protect_goal
        self.status_flag = Flags.WIP
        self.target_assignation_last_time = None
        self.target = Pose(self.game_state.field.our_goal, np.pi)  # Ignore target argument, always go for our goal
        self._find_best_passing_option()
        self.kick_force = KickForce.HIGH
        self.penalty_kick = penalty_kick

        self.tries_flag = 0
        self.grab_ball_tries = 0
        self.kick_last_time = time.time()

        self.OFFSET_FROM_GOAL_LINE = Position(ROBOT_RADIUS + 10, 0)

    def chill(self):
        position = self.game_state.field.our_goal - self.OFFSET_FROM_GOAL_LINE
        return MoveTo(Pose(position, np.pi))

    def defense_dumb(self):
        dest_y = self.game_state.ball_position.y \
                 * self.game_state.const["FIELD_GOAL_WIDTH"] / 2 / self.game_state.const["FIELD_Y_TOP"]
        position = self.game_state.field.our_goal - Position(ROBOT_RADIUS + 10, -dest_y)
        return MoveTo(Pose(position, np.pi))

    def defense(self):
        circle_radius = self.game_state.const["FIELD_GOAL_WIDTH"] / 2
        circle_center = self.game_state.field.our_goal - self.OFFSET_FROM_GOAL_LINE
        solutions = intersection_line_and_circle(circle_center,
                                                 circle_radius,
                                                 self.game_state.ball_position,
                                                 self._best_target_into_goal())
        # Their is one or two intersection on the circle, take the one on the field
        for solution in solutions:
            if solution.x < self.game_state.field.field_length / 2\
               and self.game_state.ball_position.x < self.game_state.field.field_length / 2:
                return MoveTo(Pose(solution, np.pi))

        return MoveTo(Pose(self.game_state.field.our_goal, np.pi),
                      cruise_speed=2,
                      end_speed=2)

    def _best_target_into_goal(self):
        # Find the bisectrice of the triangle made by the ball (a) and the two goals extremities(b, c)
        a = self.game_state.ball_position
        b = self.game_state.field.our_goal + Position(0, +self.game_state.const["FIELD_GOAL_WIDTH"] / 2)
        c = self.game_state.field.our_goal + Position(0, -self.game_state.const["FIELD_GOAL_WIDTH"] / 2)

        ab = a-b
        ac = a-c

        be = self.game_state.field.goal_width / (1 + ab.norm/ac.norm)

        return b + Position(0, -be)

    def debug_cmd(self):
        return [DebugCommandFactory().line(self.game_state.ball_position,
                                          self.game_state.field.our_goal - self.OFFSET_FROM_GOAL_LINE,#self._best_target_into_goal(),
                                          timeout=0.1),
                DebugCommandFactory().line(self.game_state.ball_position,
                                          self._best_target_into_goal(),
                                          timeout=0.1)]

    # def protect_goal(self):
    #     if not self.penalty_kick:
    #         if not self._is_ball_too_far and \
    #                 self.player == closest_player_to_point(self.game_state.ball_position).player and\
    #                 self._get_distance_from_ball() < ROBOT_RADIUS * 3:
    #             self.next_state = self.go_behind_ball
    #         else:
    #             self.next_state = self.protect_goal
    #         return ProtectGoal(self.game_state, self.player, self.is_yellow,
    #                            minimum_distance=300,
    #                            maximum_distance=self.game_state.const["FIELD_GOAL_RADIUS"]/2)
    #     else:
    #         our_goal = Position(self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"], 0)
    #         opponent_kicker = player_with_ball(2*ROBOT_RADIUS)
    #         ball_position = self.game_state.ball_position
    #         if opponent_kicker is not None:
    #             ball_to_goal = our_goal.x - ball_position.x
    #
    #             if self.game_state.our_side is FieldSide.POSITIVE:
    #                 opponent_kicker_orientation = clamp(opponent_kicker.pose.orientation, -pi/5, pi/5)
    #                 goalkeeper_orientation = wrap_to_pi(opponent_kicker_orientation - pi)
    #             else:
    #                 opponent_kicker_orientation = clamp(wrap_to_pi(opponent_kicker.pose.orientation - pi), -pi/5, pi/5)
    #                 goalkeeper_orientation = opponent_kicker_orientation
    #
    #             y_position_on_line = ball_to_goal * tan(opponent_kicker_orientation)
    #             width = self.game_state.const["FIELD_GOAL_WIDTH"]
    #             y_position_on_line = clamp(y_position_on_line, -width, width)
    #
    #             destination = Pose.from_values(our_goal.x, y_position_on_line, goalkeeper_orientation)
    #
    #         else:
    #             destination = Pose(our_goal)
    #         return MoveTo(destination, cruise_speed=2)

    # def kick_charge(self):
    #     self.next_state = self.protect_goal
    #     # TODO: Switch to CmdBuilder eventually
    #     return AICommand(self.player.id, kick_type=1)
    #
    # def go_behind_ball(self):
    #     if self._is_ball_too_far():
    #         self.next_state = self.protect_goal
    #
    #     # self.ball_spacing = GRAB_BALL_SPACING
    #     self.status_flag = Flags.WIP
    #     ball_position = self.game_state.ball_position
    #     orientation = (self.target.position - ball_position).angle()
    #     distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING * 3)
    #     if (self.player.pose.position - distance_behind).norm() < 100 and abs(orientation - self.player.pose.orientation) < 0.1:
    #         self.next_state = self.grab_ball
    #     else:
    #         self.next_state = self.go_behind_ball
    #         self._find_best_passing_option()
    #     ball_collision = self.tries_flag == 0
    #     return MoveTo(Pose(distance_behind, orientation),
    #                   ball_collision=ball_collision,
    #                   cruise_speed=2,
    #                   end_speed=0.2)
    #
    # def grab_ball(self):
    #     if self._is_ball_too_far():
    #         self.next_state = self.protect_goal
    #
    #     if self.grab_ball_tries == 0:
    #         if self._get_distance_from_ball() < KICK_DISTANCE:
    #             self.next_state = self.kick
    #     else:
    #         if self._get_distance_from_ball() < (KICK_DISTANCE + self.grab_ball_tries * 10):
    #             self.next_state = self.kick
    #     ball_position = self.game_state.ball_position
    #     orientation = (self.target.position - ball_position).angle()
    #     distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING)
    #     return MoveTo(Pose(distance_behind, orientation),
    #                   cruise_speed=2,
    #                   end_speed=0.3,
    #                   ball_collision=False)
    #     # charge_kick
    #     # return GoToPositionPathfinder(self.game_state, self.player, Pose(distance_behind, orientation),
    #     #                              cruise_speed=2, charge_kick=True, end_speed=0.3, collision_ball=False)
    #
    # def kick(self):
    #     # self.ball_spacing = GRAB_BALL_SPACING
    #     self.next_state = self.validate_kick
    #     self.tries_flag += 1
    #     ball_position = self.game_state.ball_position
    #     orientation = (self.target.position - ball_position).angle()
    #     return CmdBuilder()\
    #         .addMoveTo(Pose(ball_position, orientation), cruise_speed=2, end_speed=0)\
    #         .addKick(self.kick_force)\
    #         .build()
    #
    # def validate_kick(self):
    #     self.ball_spacing = GRAB_BALL_SPACING
    #     ball_position = self.game_state.ball_position
    #     orientation = (self.target.position - ball_position).angle()
    #     if self.game_state.ball_velocity.norm() > 1000 or self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD:
    #         self.next_state = self.protect_goal
    #     elif self.kick_last_time - time.time() < VALIDATE_KICK_DELAY:
    #         self.next_state = self.kick
    #     else:
    #         self.status_flag = Flags.INIT
    #         self.next_state = self.go_behind_ball
    #
    #     return CmdBuilder()\
    #         .addMoveTo(Pose(ball_position, orientation), cruise_speed=2, end_speed=0.2)\
    #         .addKick(self.kick_force)\
    #         .build()

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.ball_position).norm

    def _is_ball_too_far(self):
        our_goal = Position(self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"], 0)
        return (our_goal - self.game_state.ball_position).norm() > self.game_state.const["FIELD_GOAL_WIDTH"]

    def _is_player_towards_ball_and_target(self, abs_tol=pi/30):
        ball_position = self.game_state.ball_position
        target_to_ball = ball_position - self.target.position
        ball_to_player = self.player.pose.position - ball_position
        return compare_angle(target_to_ball.angle, ball_to_player.angle, abs_tol=abs_tol)

    def _find_best_passing_option(self):
        if (self.target_assignation_last_time is None
                or time.time() - self.target_assignation_last_time > TARGET_ASSIGNATION_DELAY):

            tentative_target_id = best_passing_option(self.player)
            if tentative_target_id is None:
                self.target = Pose(Position(self.game_state.const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)
            else:
                self.target = Pose(self.game_state.get_player_position(tentative_target_id))

            self.target_assignation_last_time = time.time()

    def get_destination_behind_ball(self, ball_spacing):
        """
            Calcule le point situé à  x pixels derrière la position 1 par rapport à la position 2
            :return: Un tuple (Pose, kick) où Pose est la destination du joueur et kick est nul (on ne botte pas)
            """

        delta_x = self.target.position.x - self.game_state.ball_position.x
        delta_y = self.target.position.y - self.game_state.ball_position.y
        theta = np.math.atan2(delta_y, delta_x)

        x = self.game_state.ball_position.x - ball_spacing * np.math.cos(theta)
        y = self.game_state.ball_position.y - ball_spacing * np.math.sin(theta)

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        if np.sqrt((player_x - x) ** 2 + (player_y - y) ** 2) < 50:
            x -= np.math.cos(theta) * 2
            y -= np.math.sin(theta) * 2
        destination_position = Position(x, y)

        return destination_position

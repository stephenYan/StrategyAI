# Under MIT license, see LICENSE.txt
from typing import List

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.area import stayOutsideCircle
from ai.Algorithm.path_partitionner import CollisionBody
from ai.STA.Tactic.enter_random_name_here import Tactic
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.states.game_state import GameState


class StayAwayFromBall(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose = Pose(),
                 keepout_radius: int = 500, args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.current_state = self.stay_out_of_circle
        self.next_state = self.stay_out_of_circle
        self.keepout_radius = keepout_radius
        self.player.collision_body_mask.append(CollisionBody.COLLIDABLE)

    def stay_out_of_circle(self):
        self.game_state.field.field_collision_body.append(
            CollisionBody(self.game_state.get_ball_position(), self.game_state.get_ball_velocity(), 500))
        position = stayOutsideCircle(self.player.pose.position,
                                     self.game_state.get_ball_position(),
                                     self.keepout_radius)
        return GoToPositionPathfinder(self.game_state, self.player, Pose(position, self.player.pose.orientation))

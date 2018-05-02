# Under MIT license, see LICENSE.txt
from functools import partial

from Util.pose import Pose

from Util.position import Position
from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random
from ai.Algorithm.evaluation_module import closest_player_to_point
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
class TestGoalKeeper(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        our_goal = self.game_state.field.our_goal_pose

        self.create_node(Role.GOALKEEPER,
                         GoalKeeper(self.game_state, self.assigned_roles[Role.GOALKEEPER], our_goal))

        attacker = self.assigned_roles[Role.FIRST_ATTACK]
        node_idle = self.create_node(Role.FIRST_ATTACK, Stop(self.game_state, attacker))
        node_go_kick = self.create_node(Role.FIRST_ATTACK, GoKick(self.game_state, attacker, target=our_goal))

        player_has_kicked = partial(self.has_kicked, attacker)

        node_idle.connect_to(node_go_kick, when=self.ball_is_outside_goal)
        node_go_kick.connect_to(node_idle, when=self.ball_is_inside_goal)
        node_go_kick.connect_to(node_go_kick, when=player_has_kicked)

    @classmethod
    def required_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.GOALKEEPER,
                                                                Role.FIRST_ATTACK]
                }

    def has_kicked(self, player):
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].current_tactic_name == 'GoKick':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False

    def ball_is_outside_goal(self):
        return not self.ball_is_inside_goal()

    def ball_is_inside_goal(self):
        return self.game_state.field.our_goal_area.point_inside(self.game_state.ball_position)

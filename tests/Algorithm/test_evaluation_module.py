
import unittest
from unittest.mock import create_autospec

import numpy as np
from Util import Pose, Position

from ai.Algorithm.evaluation_module import line_of_sight_clearance, trajectory_score
from ai.GameDomainObjects import Player
from ai.GameDomainObjects import Team
from ai.states.game_state import GameState


class TestEvaluationModule(unittest.TestCase):
    MULTIPLICATIVE_NULL_VALUE = 1
    ADDITIVE_NULL_VALUE = 0
    MAX_VALUE = 15

    def setUp(self):
        self.start_point = Position(0, 0)
        self.goal = Position(0, 0)
        self.obstacle = Position(0, 0)

    def test_obstacle_behind(self):
        self._define_points_obstacle((100, 100), (200, 200), (50, 50))

        assert trajectory_score(self.start_point, self.goal, self.obstacle) == self.MULTIPLICATIVE_NULL_VALUE

    def test_obstacle_far(self):
        self._define_points_obstacle((100, 100), (200, 200), (1500, 1500))

        assert trajectory_score(self.start_point, self.goal, self.obstacle) == self.MULTIPLICATIVE_NULL_VALUE

    def test_obstacle_on_path(self):
        self._define_points_obstacle((100, 100), (200, 200), (150, 150))

        assert trajectory_score(self.start_point, self.goal, self.obstacle) == self.MAX_VALUE

    @unittest.skip
    def test_clearance_equal_distance(self):
        player1 = build_mock_player(Position(100, 100), 1)
        player2 = build_mock_player(Position(1500, 1500), 2)
        self.goal = Position(200, 200)
        create_mock_teams({player1.id: player1, player2.id: player2}, {})

        distance_to_target = (player1.pose.position - self.goal).norm

        assert line_of_sight_clearance(player1, self.goal) == distance_to_target

    @unittest.skip
    def test_our_player_near_goal(self):
        player1 = build_mock_player(Position(100, 100), 1)
        player2 = build_mock_player(Position(130, 130), 2)
        self.goal.x, self.goal.y = (200, 200)
        create_mock_teams({player1.id: player1, player2.id: player2}, {})

        distance_to_target = np.linalg.norm(player1.pose.position - self.goal)
        path_score = trajectory_score(player1.pose.position, self.goal, player2.pose.position)

        assert line_of_sight_clearance(player1, self.goal) == distance_to_target * path_score

    @unittest.skip
    def test_two_our_player_near_goal(self):
        player1 = build_mock_player(Position(100, 100), 1)
        player2 = build_mock_player(Position(130, 130), 2)
        player3 = build_mock_player(Position(160, 170), 3)
        self.goal.x, self.goal.y = (200, 200)
        create_mock_teams({player1.id: player1, player2.id: player2, player3.id: player3}, {})

        distance_to_target = np.linalg.norm(player1.pose.position - self.goal)
        path_score_to_p2 = trajectory_score(player1.pose.position, self.goal, player2.pose.position)
        path_score_to_p3 = trajectory_score(player1.pose.position, self.goal, player3.pose.position)

        assert line_of_sight_clearance(player1, self.goal) == distance_to_target * path_score_to_p2 * path_score_to_p3

    @unittest.skip
    def test_enemy_player_far_distance(self):
        player1 = build_mock_player(Position(100, 100), 1)
        player2 = build_mock_player(Position(1500, 1500), 2)
        self.goal.x, self.goal.y = (200, 200)
        create_mock_teams({player1.id: player1}, {2: player2})

        distance_to_target = np.linalg.norm(player1.pose.position - self.goal)

        assert line_of_sight_clearance(player1, self.goal) == distance_to_target

    @unittest.skip
    def test_enemy_player_near_goal(self):
        player1 = build_mock_player(Position(100, 100), 1)
        player2 = build_mock_player(Position(130, 130), 2)
        self.goal.x, self.goal.y = (200, 200)
        create_mock_teams({player1.id: player1}, {2: player2})

        distance_to_target = np.linalg.norm(player1.pose.position - self.goal)
        path_score = trajectory_score(player1.pose.position, self.goal, player2.pose.position)

        assert line_of_sight_clearance(player1, self.goal) == distance_to_target * path_score

    @unittest.skip
    def test_two_enemy_near_goal(self):
        player1 = build_mock_player(Position(100, 100), 1)
        player2 = build_mock_player(Position(130, 130), 2)
        player3 = build_mock_player(Position(160, 170), 3)
        self.goal.x, self.goal.y = (200, 200)
        create_mock_teams({player1.id: player1}, {player2.id: player2, player3.id: player3})

        distance_to_target = np.linalg.norm(player1.pose.position - self.goal)
        path_score_to_p2 = trajectory_score(player1.pose.position, self.goal, player2.pose.position)
        path_score_to_p3 = trajectory_score(player1.pose.position, self.goal, player3.pose.position)

        assert line_of_sight_clearance(player1, self.goal) == distance_to_target * path_score_to_p2 * path_score_to_p3

    def _define_points_obstacle(self, start_point, goal, obstacle):
        self.start_point.x, self.start_point.y = start_point
        self.goal.x, self.goal.y = goal
        self.obstacle.x, self.obstacle.y = obstacle


def build_mock_player(position, pid):
    player = create_autospec(Player)
    pose = create_autospec(Pose)
    pose.position = position
    player.pose = pose
    player.id = pid
    return player


def create_mock_teams(allies, opponents):
    team1 = create_autospec(Team)
    team1.available_players = allies
    # pylint: disable=protected-access
    GameState()._our_team = team1
    print(GameState().our_team.available_players.values())

    team2 = create_autospec(Team)
    # pylint: disable=protected-access
    team2.available_players = opponents
    GameState()._enemy_team = team2

# Under MIT licence, see LICENCE.txt
import math
from .Action import Action
from ...Util.types import AICommand
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import *
from RULEngine.Util.area import stayInsideCircle, stayOutsideCircle, stayInsideGoalArea
from RULEngine.Util.geometry import get_angle
#from RULEngine.Util.geometry import get_closest_point_on_line

__author__ = 'Robocup ULaval'


class ProtectGoal(Action):
    """
    Action ProtectGoal: Action de base pour le gardien de but. D�place le gardien entre la balle et le centre du but, �
    une certaine distance de celui-ci, tout en restant dans la zone du gardien.
    M�thodes:
        exec(self): Retourne la pose o� se rendre.
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du gardien.
        is_right_goal : Un bool�en indiquant si le but � prot�ger est celui de droite.
        minimum_distance : La distance minimale qu'il doit y avoir entre le gardien et le centre du but.
        maximum_distance : La distance maximale qu'il doit y avoir entre le gardien et le centre du but.
    """
    def __init__(self, p_info_manager, p_player_id, p_is_right_goal=True, p_minimum_distance=FIELD_GOAL_RADIUS/2,
                 p_maximum_distance=None):
        """
        :param p_info_manager: Une r�f�rence vers l'InfoManager.
        :param p_player_id: L'identifiant du joueur qui est le gardien de but.
        :param p_is_right_goal: Un bool�en indiquant si le but � prot�ger est celui de droite.
        :param p_minimum_distance: La distance minimale qu'il doit y avoir entre le gardien et le centre du but.
        :param p_maximum_distance: La distance maximale qu'il doit y avoir entre le gardien et le centre du but.
        """
        Action.__init__(self, p_info_manager)
        assert isinstance(p_player_id, int)
        assert isinstance(p_is_right_goal, bool)
        assert isinstance(p_minimum_distance, (int, float))
        assert isinstance(p_maximum_distance, (int, float, None))
        if p_maximum_distance is not None:
            assert p_maximum_distance >= p_minimum_distance

        self.player_id = p_player_id
        self.is_right_goal = p_is_right_goal
        self.minimum_distance = p_minimum_distance
        self.maximum_distance = p_maximum_distance

    def exec(self):
        """
        Calcul la pose que doit prendre le gardien en fonction de la position de la balle.
        :return: Un tuple (Pose, kick) o� Pose est la destination du gardien et kick est nul (on ne botte pas)
        """
        goalkeeper_position = self.info_manager.get_player_pose(self.player_id).position
        ball_position = self.info_manager.get_ball_position()
        goal_x = FIELD_X_RIGHT if self.is_right_goal else FIELD_X_LEFT
        goal_position = Position(goal_x, 0)

        # Calcul de la position pour d'interception entre la balle et le centre du but
        destination_position = Position()
        #destination_position = get_closest_point_on_line(goalkeeper_position, goal_position, ball_position)

        # V�rification que destination_position respecte la distance minimale
        destination_position = stayOutsideCircle(destination_position, goal_position, self.minimum_distance)

        # V�rification que destination_position respecte la distance maximale
        if self.maximum_distance is None:
            destination_position = stayInsideGoalArea(destination_position, self.is_right_goal)
        else:
            destination_position = stayInsideCircle(destination_position, goal_position, self.maximum_distance)

        # Calcul de l'orientation de la pose de destination
        destination_orientation = get_angle(destination_position, ball_position)

        destination_pose = Pose(destination_position, destination_orientation)
        kick_strength = 0
        return AICommand(destination_pose, kick_strength)

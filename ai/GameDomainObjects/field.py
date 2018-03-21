from typing import Dict

from Util import Position
from ai.GameDomainObjects import Ball


class Field:
    def __init__(self, ball: Ball):

        self._ball = ball
        self._constant = constant

    @property
    def ball(self):
        if not self._ball:
            raise RuntimeError('There is no ball to detect')
        return self._ball

    @property
    def constant(self):
        return self._constant

    @constant.setter
    def constant(self, field: Dict):
        self._constant["FIELD_Y_TOP"] = self._field_width / 2
        self._constant["FIELD_Y_BOTTOM"] = -self._field_width / 2
        self._constant["FIELD_X_LEFT"] = -self._field_length / 2
        self._constant["FIELD_X_RIGHT"] = self._field_length / 2

        self._constant["CENTER_CENTER_RADIUS"] = self._center_circle_radius

        self._constant["FIELD_Y_POSITIVE"] = self._field_width / 2
        self._constant["FIELD_Y_NEGATIVE"] = -self._field_width / 2
        self._constant["FIELD_X_NEGATIVE"] = -self._field_length / 2
        self._constant["FIELD_X_POSITIVE"] = self._field_length / 2

        self._constant["FIELD_BOUNDARY_WIDTH"] = self._boundary_width

        self._constant["FIELD_GOAL_RADIUS"] = self._defense_radius
        self._constant["FIELD_GOAL_SEGMENT"] = self._defense_stretch
        self._constant["FIELD_GOAL_WIDTH"] = self._goal_width

        self._constant["FIELD_GOAL_Y_TOP"] = self._defense_radius + (self._defense_stretch / 2)
        self._constant["FIELD_GOAL_Y_BOTTOM"] = -self._constant["FIELD_GOAL_Y_TOP"]

        if self.our_side == FieldSide.POSITIVE:
            self._constant["FIELD_THEIR_GOAL_X_EXTERNAL"] = self._constant["FIELD_X_NEGATIVE"]
            self._constant["FIELD_THEIR_GOAL_X_INTERNAL"] = self._constant["FIELD_X_NEGATIVE"] + self._constant[
                "FIELD_GOAL_RADIUS"]

            self._constant["FIELD_OUR_GOAL_X_INTERNAL"] = self._constant["FIELD_X_POSITIVE"] - self._constant[
                "FIELD_GOAL_RADIUS"]
            self._constant["FIELD_OUR_GOAL_X_EXTERNAL"] = self._constant["FIELD_X_POSITIVE"]

            self._constant["FIELD_THEIR_GOAL_TOP_CIRCLE"] = Position(self._constant["FIELD_X_NEGATIVE"],
                                                                    self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"] = Position(self._constant["FIELD_X_NEGATIVE"],
                                                                       -self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_THEIR_GOAL_MID_GOAL"] = Position(self._constant["FIELD_X_NEGATIVE"], 0)

            self._constant["FIELD_OUR_GOAL_TOP_CIRCLE"] = Position(self._constant["FIELD_X_POSITIVE"],
                                                                  self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] = Position(self._constant["FIELD_X_POSITIVE"],
                                                                     -self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_OUR_GOAL_MID_GOAL"] = Position(self._constant["FIELD_X_POSITIVE"], 0)

        else:
            self._constant["FIELD_OUR_GOAL_X_EXTERNAL"] = self._constant["FIELD_X_NEGATIVE"]
            self._constant["FIELD_OUR_GOAL_X_INTERNAL"] = self._constant["FIELD_X_NEGATIVE"] + self._constant[
                "FIELD_GOAL_RADIUS"]

            self._constant["FIELD_THEIR_GOAL_X_INTERNAL"] = self._constant["FIELD_X_POSITIVE"] - self._constant[
                "FIELD_GOAL_RADIUS"]
            self._constant["FIELD_THEIR_GOAL_X_EXTERNAL"] = self._constant["FIELD_X_POSITIVE"]

            self._constant["FIELD_OUR_GOAL_TOP_CIRCLE"] = Position(self._constant["FIELD_X_NEGATIVE"],
                                                                  self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] = Position(self._constant["FIELD_X_NEGATIVE"],
                                                                     -self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_OUR_GOAL_MID_GOAL"] = Position(self._constant["FIELD_X_NEGATIVE"], 0)

            self._constant["FIELD_THEIR_GOAL_TOP_CIRCLE"] = Position(self._constant["FIELD_X_POSITIVE"],
                                                                    self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"] = Position(self._constant["FIELD_X_POSITIVE"],
                                                                       -self._constant["FIELD_GOAL_SEGMENT"] / 2)
            self._constant["FIELD_THEIR_GOAL_MID_GOAL"] = Position(self._constant["FIELD_X_POSITIVE"], 0)
        
        
        
        
        


constant = {
    # Field Parameters
    "FIELD_Y_TOP": 3000,
    "FIELD_Y_BOTTOM": -3000,
    "FIELD_X_LEFT": -4500,
    "FIELD_X_RIGHT": 4500,

    "CENTER_CENTER_RADIUS": 1000,

    "FIELD_Y_POSITIVE": 3000,
    "FIELD_Y_NEGATIVE": -3000,
    "FIELD_X_NEGATIVE": -4500,
    "FIELD_X_POSITIVE": 4500,

    "FIELD_BOUNDARY_WIDTH": 700,

    "FIELD_GOAL_RADIUS": 1000,
    "FIELD_GOAL_SEGMENT": 500,

    # Goal Parameters
    "FIELD_GOAL_WIDTH": 1000,
    "FIELD_GOAL_Y_TOP": 1250,  # FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2
    "FIELD_GOAL_Y_BOTTOM": -1250,  # (FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2) * -1
    "FIELD_OUR_GOAL_X_EXTERNAL": 4500,  # FIELD_X_LEFT
    "FIELD_OUR_GOAL_X_INTERNAL": 3500,  # FIELD_X_LEFT + FIELD_GOAL_RADIUS
    "FIELD_THEIR_GOAL_X_INTERNAL": -3500,  # FIELD_X_RIGHT - FIELD_GOAL_RADIUS
    "FIELD_THEIR_GOAL_X_EXTERNAL": -4500,  # FIELD_X_RIGHT

    "FIELD_DEFENSE_PENALTY_MARK": Position(1, 0),
    "FIELD_OFFENSE_PENALTY_MARK": Position(1, 0),

    # Field Positions
    "FIELD_OUR_GOAL_TOP_CIRCLE": Position(4500, 250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_OUR_GOAL_BOTTOM_CIRCLE": Position(4500, -250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_OUR_GOAL_MID_GOAL": Position(4500, 0),
    "FIELD_THEIR_GOAL_TOP_CIRCLE": Position(-4500, 250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_THEIR_GOAL_BOTTOM_CIRCLE": Position(-4500, -250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_THEIR_GOAL_MID_GOAL": Position(-4500, 0),

    # Legal field dimensions
    "LEGAL_Y_TOP": 3000,
    # LEGAL_Y_TOP": 0
    "LEGAL_Y_BOTTOM": -3000,
    "LEGAL_X_LEFT": -4500,
    "LEGAL_X_RIGHT": 4500,
    # LEGAL_X_RIGHT": 0
}

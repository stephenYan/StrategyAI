# Under MIT License, see LICENSE.txt

__author__ = "Maxime Gagnon-Legault, Philippe Babin"

from typing import Dict

from Util.pose import Pose
from Util.position import Position


class Ball:
    def __init__(self, id):
        self._id = id
        self._position = Position()
        self._velocity = Position()

    def update(self, new_position: Position, new_velocity: Position):
        self.position = new_position
        self.velocity = new_velocity

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value) -> None:
        assert isinstance(value, int)
        assert 0 <= value
        self._id = value

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, value) -> None:
        assert isinstance(value, Position)
        self._position = value

    @property
    def velocity(self) -> Position:
        return self._velocity

    @velocity.setter
    def velocity(self, value) -> None:
        assert isinstance(value, Position)
        self._velocity = value

    @classmethod
    def from_dict(cls, dict: Dict):
        b = Ball(dict["id"])
        b.position = Position.from_dict(dict["pose"])
        b.velocity.x = dict["velocity"]["x"]
        b.velocity.y = dict["velocity"]["y"]
        return b

import numpy as np

from RULEngine.robot import Robot
from Util import Position, Pose

MIN_DISTANCE_TO_REACH_TARGET_SPEED = 10


def get_next_velocity(robot: Robot, dt):
    """Return the next velocity according to a constant acceleration model of a point mass.
       It try to produce a trapezoidal velocity path with the required cruising and target speed.
       The target speed is the speed that the robot need to reach at the target point."""
    next_speed = Pose.from_dict(robot.velocity).position.norm()
    target_speed = robot.path.speeds[1]
    cruise_speed = robot.cruise_speed
    target_direction = robot.path.turns[1].normalized()
    if target_reached(robot, target_speed, next_speed):  # We need to go to target speed
        if next_speed < target_speed:  # Target speed is faster than current speed
            next_speed += robot.max_linear_acceleration * dt
            if next_speed > target_speed:  # Next_speed is too fast
                next_speed = target_speed
        else:  # Target speed is slower than current speed
            next_speed -= robot.max_linear_acceleration * dt *2
    else:  # We need to go to the cruising speed
        print(cruise_speed)
        if next_speed < cruise_speed:  # Going faster
            next_speed += robot.max_linear_acceleration * dt
            # next_speed = min(cruise_speed, next_speed)
        else:
            next_speed -= robot.max_linear_acceleration * dt * 2


    next_speed = np.clip(next_speed, 0.0, robot.max_linear_speed)
    next_velocity = Position(target_direction * next_speed)

    return next_velocity


def target_reached(robot: Robot, target_speed, current_speed) -> bool:  # distance_to_reach_target_speed

    distance = 0.5 * (target_speed ** 2 - current_speed ** 2) / robot.max_linear_acceleration
    distance = max(distance, MIN_DISTANCE_TO_REACH_TARGET_SPEED)
    position_error = robot.path.points[1] - Pose.from_dict(robot.pose).position

    return position_error.norm() <= distance
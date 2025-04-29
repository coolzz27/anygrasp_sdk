#!/usr/bin/env python

"""basics3_primitive_execution.py

This tutorial executes several basic robot primitives (unit skills). For detailed documentation
on all available primitives, please see [Flexiv Primitives](https://www.flexiv.com/primitives/).
"""

__copyright__ = "Copyright (C) 2016-2024 Flexiv Ltd. All Rights Reserved."
__author__ = "Flexiv"

import time
import argparse
import spdlog  # pip install spdlog

# Utility methods
from utility import quat2eulerZYX
from utility import list2str

# Flexiv RDK Python library is installed to user site packages
import flexivrdk


def arm_move(translation, rotation):
    # Program Setup
    # ==============================================================================================
    robot_sn = "Rizon4-062516"

    # Define alias
    logger = spdlog.ConsoleLogger("Example")
    mode = flexivrdk.Mode

    try:
        # RDK Initialization
        # ==========================================================================================
        # Instantiate robot interface
        robot = flexivrdk.Robot(robot_sn)

        # Clear fault on the connected robot if any
        if robot.fault():
            logger.warn(
                "Fault occurred on the connected robot, trying to clear ...")
            # Try to clear the fault
            if not robot.ClearFault():
                logger.error("Fault cannot be cleared, exiting ...")
                return 1
            logger.info("Fault on the connected robot is cleared")

        # Enable the robot, make sure the E-stop is released before enabling
        logger.info("Enabling robot ...")
        robot.Enable()

        # Wait for the robot to become operational
        while not robot.operational():
            time.sleep(1)

        logger.info("Robot is now operational")

        # Execute Primitives
        # ==========================================================================================
        # Switch to primitive execution mode
        robot.SwitchMode(mode.NRT_PRIMITIVE_EXECUTION)

        # (1) Go to home pose
        # ------------------------------------------------------------------------------------------
        # All parameters of the "Home" primitive are optional, thus we can skip the parameters and
        # the default values will be used
        # logger.info("Executing primitive: Home")

        # # Send command to robot
        robot.ExecutePrimitive("Home", dict())

        # Wait for reached target
        # Note: primitive_states() returns a dictionary of {pt_state_name, [pt_state_values]}
        while not robot.primitive_states()["reachedTarget"]:
            time.sleep(1)

        # (3) Move robot TCP to a target position in world (base) frame
        # ------------------------------------------------------------------------------------------
        # Required parameter:
        #   target: final target position
        #       [pos_x pos_y pos_z rot_x rot_y rot_z ref_frame ref_point]
        #       Unit: m, deg
        # Optional parameter:
        #   waypoints: waypoints to pass before reaching final target
        #       (same format as above, but can repeat for number of waypoints)
        #   vel: TCP linear velocity
        #       Unit: m/s
        # NOTE: The rotations use Euler ZYX convention, rot_x means Euler ZYX angle around X axis
        logger.info("Executing primitive: MoveL")

        # Send command to robot
        robot.ExecutePrimitive(
            "MoveL",
            {
                "target": flexivrdk.Coord(
                    [translation[0], translation[1], 0.3], rotation, [
                        "WORLD", "WORLD_ORIGIN"]
                ),
                "waypoints": [
                    flexivrdk.Coord(
                        [translation[0], translation[1], 0.3], rotation, [
                            "WORLD", "WORLD_ORIGIN"]
                    ),
                    flexivrdk.Coord(
                        translation, rotation, ["WORLD", "WORLD_ORIGIN"]
                    ),
                ],
                "vel": 0.6,
                "zoneRadius": "Z50",
            },
        )

        while not robot.primitive_states()["reachedTarget"]:
            time.sleep(1)

        robot.ExecutePrimitive("Home", dict())
        # Wait for reached target
        # Note: primitive_states() returns a dictionary of {pt_state_name, [pt_state_values]}
        while not robot.primitive_states()["reachedTarget"]:
            time.sleep(1)

        robot.Stop()

    except Exception as e:
        # Print exception error message
        logger.error(str(e))


if __name__ == "__main__":
    arm_move()

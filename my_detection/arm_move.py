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

        # Instantiate gripper control interface
        gripper = flexivrdk.Gripper(robot)

        # Manually initialize the gripper, not all grippers need this step
        # logger.info(
        #     "Initializing gripper, this process takes about 10 seconds ...")
        # gripper.Init()
        # time.sleep(10)
        # logger.info("Initialization complete")

        # (1) Go to home pose
        robot.ExecutePrimitive("Home", dict())
        logger.info("Opening gripper")
        gripper.Move(0.1, 0.2, 20)
        time.sleep(2)

        # Wait for reached target
        while not robot.primitive_states()["reachedTarget"]:
            time.sleep(1)

        # (3) Move robot TCP to a target position in world (base) frame
        logger.info("Executing primitive: MoveL")

        # Send command to robot
        robot.ExecutePrimitive(
            "MoveL",
            {
                "target": flexivrdk.Coord(
                    translation, rotation, [
                        "WORLD", "WORLD_ORIGIN"]
                ),
                "waypoints": [
                    flexivrdk.Coord(
                        [translation[0], translation[1], translation[2]+0.05], rotation, [
                            "WORLD", "WORLD_ORIGIN"]
                    ),
                ],
                "vel": 0.1,
                "zoneRadius": "Z50",
            },
        )

        while not robot.primitive_states()["reachedTarget"]:
            time.sleep(1)

        logger.info("Closing gripper")
        gripper.Move(0, 0.2, 10)
        time.sleep(2)

        robot.ExecutePrimitive(
            "MoveL",
            {
                "target": flexivrdk.Coord(
                    [translation[0], translation[1], translation[2]+0.05], rotation, [
                        "WORLD", "WORLD_ORIGIN"]
                ),
                "vel": 0.1,
            },
        )
        while not robot.primitive_states()["reachedTarget"]:
            time.sleep(1)

        robot.ExecutePrimitive("Home", dict())
        while not robot.primitive_states()["reachedTarget"]:
            time.sleep(1)

        logger.info("Opening gripper")
        gripper.Move(0.1, 0.2, 20)
        time.sleep(2)

        robot.Stop()

    except Exception as e:
        # Print exception error message
        logger.error(str(e))


if __name__ == "__main__":
    arm_move()

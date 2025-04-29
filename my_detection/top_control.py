import numpy as np
import subprocess
import json

from get_grasp import get_grasp
from svo_record import svo_record
from svo_export import svo_export
from rot_convert import rotation_matrix_to_euler
# from arm_move import arm_move


def call_arm_move(translation, rotation):
    """通过子进程调用另一个conda环境中的arm_move"""
    input_data = {
        "translation": translation.tolist(),
        "rotation": rotation.tolist()
    }

    cmd = [
        "conda", "run", "-n", "flexiv",
        "python", "arm_move_script.py",
        json.dumps(input_data)
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    raise RuntimeError(f"{result.stdout}")


R_cam2base = np.array([
    [-0.25811838, 0.81660416, -0.51626791],
    [0.96590179, 0.22930709, -0.12021642],
    [0.02021467, -0.52969416, -0.84794779]
])
t_cam2base = np.array([[0.6639729, -0.19698481, 0.4085248]])

H_cam2base = np.eye(4)
H_cam2base[:3, :3] = R_cam2base
H_cam2base[:3, 3] = t_cam2base

svo_record()
svo_export()

gripper = get_grasp('data')
gripper_R_cam = gripper.rotation_matrix
gripper_t_cam = gripper.translation

gripper_H_cam = np.eye(4)
gripper_H_cam[:3, :3] = gripper_R_cam
gripper_H_cam[:3, 3] = gripper_t_cam

gripper_H_base = H_cam2base @ gripper_H_cam
print(gripper_H_base)

gripper_R_base = gripper_H_base[:3, :3]
gripper_t_base = gripper_H_base[:3, 3]


rotation = rotation_matrix_to_euler(gripper_R_base)
print("translation: ", gripper_t_base)
print("rotation: ", rotation)
gripper_t_base[2] += 0.25
rotation = np.array([180, 0, 180]).flatten()
# arm_move(gripper_t_base, rotation)

try:
    call_arm_move(gripper_t_base, rotation)
except Exception as e:
    print(f"{e}")

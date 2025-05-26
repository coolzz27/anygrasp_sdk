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
    [-0.00656869,  0.77954296, -0.62631432],
    [0.99936014, -0.01690407, -0.03152081],
    [-0.03515909, -0.62612061, -0.77893313]
])
t_cam2base = np.array([[0.76953153, -0.36666019, 0.57201938]])

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
gripper_t_base[2] += 0.15
if gripper_t_base[2] < 0.2:
    gripper_t_base[2] = 0.23
    print("[Warning] height is dangerous")

gripper_t_base[0] -= 0.02
gripper_t_base[1] += 0.03

rotation[0] = 180
rotation[1] = 0
# rotation = np.array([180, 0, 180]).flatten()

try:
    call_arm_move(gripper_t_base, rotation)
except Exception as e:
    print(f"{e}")

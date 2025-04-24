import numpy as np

from get_grasp import get_grasp

R_cam2base = np.array([
    [-0.25811838, 0.81660416, -0.51626791],
    [0.96590179, 0.22930709, -0.12021642],
    [0.02021467, -0.52969416, -0.84794779]
])
t_cam2base = np.array([[0.6639729], [-0.19698481], [0.4085248]])

H_cam2base = np.eye(4)
H_cam2base[:3, :3] = R_cam2base
H_cam2base[:3, 3] = t_cam2base

gripper = get_grasp('data')
gripper_R_cam = gripper.rotation_matrix
gripper_t_cam = gripper.translation

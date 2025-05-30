import os
import argparse
import torch
import numpy as np
import open3d as o3d
from PIL import Image
from types import SimpleNamespace

from rot_convert import rotation_matrix_to_euler

from gsnet import AnyGrasp
from graspnetAPI import GraspGroup



def get_grasp(data_dir):
    cfgs = SimpleNamespace(
        checkpoint_path="log/checkpoint_detection.tar",
        max_gripper_width=0.1,
        gripper_height=0.1,
        top_down_grasp=True,
        debug=True
    )

    anygrasp = AnyGrasp(cfgs)
    anygrasp.load_net()

    # get data
    colors = np.array(Image.open(os.path.join(
        data_dir, 'color.png')).convert('RGB'), dtype=np.float32) / 255.0
    depths = np.array(Image.open(os.path.join(data_dir, 'depth.png')))
    # get camera intrinsics
    # fx, fy = 957.135, 957.625
    # cx, cy = 641.665, 361.891
    fx, fy = 1914.27, 1915.25
    cx, cy = 1110.33, 627.782
    scale = 1000.0
    # set workspace to filter output grasps
    xmin, xmax = -0.2, 0.2
    ymin, ymax = -0.2, 0.15
    zmin, zmax = 0.0, 1.0
    lims = [xmin, xmax, ymin, ymax, zmin, zmax]

    # get point cloud
    xmap, ymap = np.arange(depths.shape[1]), np.arange(depths.shape[0])
    xmap, ymap = np.meshgrid(xmap, ymap)
    points_z = depths / scale
    points_x = (xmap - cx) / fx * points_z
    points_y = (ymap - cy) / fy * points_z

    # set your workspace to crop point cloud
    mask = (points_z > 0) & (points_z < 1)
    points = np.stack([points_x, points_y, points_z], axis=-1)
    points = points[mask].astype(np.float32)
    colors = colors[mask].astype(np.float32)
    print(points.min(axis=0), points.max(axis=0))

    gg, cloud = anygrasp.get_grasp(
        points, colors, lims=lims, apply_object_mask=True, dense_grasp=False, collision_detection=True)

    if len(gg) == 0:
        print('No Grasp detected after collision detection!')

    gg = gg.nms().sort_by_score()
    gg_pick = gg[0:20]
    rot_angles = rotation_matrix_to_euler(gg_pick[0].rotation_matrix)
    print("grasp info:", rot_angles, gg_pick[0].translation)
    print('grasp score:', gg_pick[0].score)

    # visualization
    if cfgs.debug:
        trans_mat = np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
        cloud.transform(trans_mat)
        grippers = gg.to_open3d_geometry_list()
        for gripper in grippers:
            gripper.transform(trans_mat)
        # o3d.visualization.draw_geometries([*grippers, cloud])
        o3d.visualization.draw_geometries([grippers[0], cloud])

    return gg_pick[0]


if __name__ == '__main__':

    get_grasp('./data/')

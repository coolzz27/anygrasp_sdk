import numpy as np
import cv2
import scipy
import os

def euler_to_rotation_matrix(angles):
    angles_rad = np.radians(angles)

    roll, pitch, yaw = angles_rad

    R_x = np.array([[1, 0, 0],
                    [0, np.cos(roll), -np.sin(roll)],
                    [0, np.sin(roll), np.cos(roll)]])

    R_y = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                    [0, 1, 0],
                    [-np.sin(pitch), 0, np.cos(pitch)]])

    R_z = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                    [np.sin(yaw), np.cos(yaw), 0],
                    [0, 0, 1]])

    R = R_z @ R_y @ R_x
    return R

def calibrate_eye_hand(R_gripper2base, t_gripper2base, R_target2cam, t_target2cam, eye_to_hand=True):

    if eye_to_hand:
        # change coordinates from gripper2base to base2gripper
        R_base2gripper, t_base2gripper = [], []
        for R, t in zip(R_gripper2base, t_gripper2base):
            R_b2g = R.T
            t_b2g = -R_b2g @ t
            R_base2gripper.append(R_b2g)
            t_base2gripper.append(t_b2g)

    # calibrate
    R, t = cv2.calibrateHandEye(
        R_base2gripper,
        t_base2gripper,
        R_target2cam,
        t_target2cam
    )

    return R, t

mtx = np.array([
    [1.85391319e+03, 0.00000000e+00, 1.12117879e+03],
    [0.00000000e+00, 1.86448545e+03, 7.22642502e+02],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
])

dist = np.array([[-0.07672638, 0.0087316, 0.00864253, 0.00472594, -0.24129789]])


if __name__ == "__main__":
    image_folder = '.'
    chessboard_size = (8, 6)
    square_size = 0.0251  # meters

    images = []
    for i in range(1, 12):
        img_path = f"images/new_{i}.png"
        img = cv2.imread(img_path)
        img_undistorted = cv2.undistort(img, mtx, dist)
        images.append(img_undistorted)

    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0],
                           0:chessboard_size[1]].T.reshape(-1, 2) * square_size

    output_file = "target_to_cam.txt"
    cnt = 0
    R_target2cam = []
    t_target2cam = []
    with open(output_file, 'w') as f:
        for img in images:
            cnt = cnt + 1
            ret, corners = cv2.findChessboardCorners(
                img, chessboard_size, None)

            if ret:
                # Refine corner positions
                corners2 = cv2.cornerSubPix(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), corners, (11, 11), (-1, -1),
                                            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
                # cv2.drawChessboardCorners(img, chessboard_size, corners2, ret)
                # cv2.imshow('img', img)
                # cv2.waitKey(0)

                success, rvec, tvec = cv2.solvePnP(
                    objp, corners2, mtx, None)
                R_target2cam.append(rvec)
                t_target2cam.append(tvec)

                R, _ = cv2.Rodrigues(rvec)
                proj_matrix = np.hstack((R, tvec))
                eulerAngles = -cv2.decomposeProjectionMatrix(proj_matrix)[6]
                yaw = eulerAngles[1][0]
                pitch = eulerAngles[0][0]
                roll = eulerAngles[2][0]
                # if cnt == 1: print(R_new)

                f.write(f"eye,{tvec[0][0]},{tvec[1][0]},{tvec[2][0]},{roll},{pitch},{yaw}\n")
                # f.write(f"eye,{tvec[0][0]:.2f},{tvec[1][0]:.2f},{tvec[2][0]:.2f},{yaw:.2f},{pitch:.2f},{roll:.2f}\n")

            else:
                print("Warning: Chessboard not found in image!")

    # print(f"结果已保存至 {output_file}")

    poses = []
    with open('hand.txt', 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            
            if len(parts) == 7:
                try:
                    x = float(parts[1])
                    y = float(parts[2])
                    z = float(parts[3])
                    rx = float(parts[4])
                    ry = float(parts[5])
                    rz = float(parts[6])

                    poses.append((x, y, z, rx, ry, rz))
                    
                except ValueError:
                    print(f"数值转换失败，跳过行: {line.strip()}")

    R_gripper2base = []
    t_gripper2base = []
    for pose in poses:
        t = pose[0:3]
        angles = pose[3:]
        R = euler_to_rotation_matrix(angles)

        R_gripper2base.append(R)
        t_gripper2base.append(t)

    R_cam2base, t_cam2base = calibrate_eye_hand(R_gripper2base, t_gripper2base, R_target2cam, t_target2cam)

    print(f"R_cam2base:\n{R_cam2base}\nt_cam2base:\n{t_cam2base}")

    # pos_cam = t_target2cam[2]
    # pos_base = R_cam2base @ pos_cam + t_cam2base
    # print(f"pos_base: {pos_base}")

import cv2
import numpy as np

# 内参矩阵 [fx, 0, cx; 0, fy, cy; 0, 0, 1]
camera_matrix = np.array([
    [1.85391319e+03, 0.00000000e+00, 1.12117879e+03],
    [0.00000000e+00, 1.86448545e+03, 7.22642502e+02],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
])

# 畸变系数 [k1, k2, p1, p2, k3]
dist_coeffs = np.array([
    [-0.07672638, 0.0087316, 0.00864253, 0.00472594, -0.24129789]
])


def undistort_image(img_path):
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"无法读取图像: {img_path}")

    undistorted_img = cv2.undistort(img,
                                    camera_matrix,
                                    dist_coeffs,
                                    None,
                                    camera_matrix)

    comparison = np.hstack((img, undistorted_img))

    # 显示结果
    cv2.imshow('Original vs Undistorted', comparison)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


undistort_image("./processed_images/Explorer_HD2K_SN30856488_19-53-10.png")

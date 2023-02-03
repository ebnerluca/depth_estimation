#!/usr/bin/python3

# This script can be used to visually compare an image and its corresponding depth img

import cv2
import numpy as np
from os.path import join
import matplotlib.pyplot as plt


#########################################

LAPLACIAN_CUTOFF = 1.0  # values higher than ~5 mean cutoff has almost no effect
USE_LAPLACIAN_CUTOFF = False

project_folder = "/media/auv/Seagate_2TB/datasets/r20221105_053256_lizard_d2_048_resort"
img_folder = "i20221105_053256_cv"
exported_depths_folder = "exported_depth_f32"
img_name = "PR_20221105_053300_930_LC16"

img_path = join(project_folder, img_folder, img_name) + ".png"
# depth_path = join(project_folder, exported_depths_folder, img_name) + "_rendered.png"
depth_path = join(project_folder, exported_depths_folder, img_name) + ".tif"
# depth_path = join(project_folder, exported_depths_folder, img_name) + "_undistorted.tif"

#########################################


# load imgs
img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
depth = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)

# create depth heatmap for visualization
tmp_min = np.amin(depth[depth > 0.0])
tmp_range = np.amax(depth) - tmp_min
depth_n = (depth - tmp_min) / tmp_range
colormap = plt.get_cmap("inferno")
depth_n = (colormap(1.0 - depth_n) * 255).astype(np.uint8)[:, :, :3]
depth_n = cv2.cvtColor(depth_n, cv2.COLOR_RGB2BGR)

# print stats
img_dimensions = img.shape
depth_dimensions = depth.shape
depth_n_dimensions = depth_n.shape
print(f"img_dimensions: {img_dimensions}")
print(f"depth_dimensions: {depth_dimensions}")
print(f"depth_n_dimensions: {depth_n_dimensions}")
print(f"depth range: [{np.amin(depth)}, {np.amax(depth)}]")

# create laplacian for overlay
laplacian = cv2.Laplacian(depth, cv2.CV_32FC1)
laplacian = np.abs(laplacian)
if USE_LAPLACIAN_CUTOFF:
    laplacian[
        laplacian > LAPLACIAN_CUTOFF
    ] = 0.0  # dont use big gradiants coming from boundary
laplacian = cv2.normalize(laplacian, None, 0, 1.0, cv2.NORM_MINMAX)
laplacian = cv2.cvtColor(laplacian, cv2.COLOR_GRAY2BGR)
laplacian[:, :, 0] = 0.0  # set blue to zero
laplacian[:, :, 1] = 0.0  # set green to zero

# resize
depth = cv2.resize(depth, (img_dimensions[1], img_dimensions[0]))
depth_n = cv2.resize(depth_n, (img_dimensions[1], img_dimensions[0]))
laplacian = cv2.resize(laplacian, (img_dimensions[1], img_dimensions[0]))

# create overlay with laplacian
overlay_laplacian = cv2.addWeighted(
    cv2.cvtColor(img, cv2.COLOR_GRAY2BGR), 0.5, np.uint8(laplacian * 255), 0.5, 0
)

# create overlay with depth heatmap
overlay_depth = cv2.addWeighted(
    cv2.cvtColor(img, cv2.COLOR_GRAY2BGR), 0.7, depth_n, 0.3, 0
)

# visualize
cv2.imshow("image", img)
cv2.imshow("depth heatmap", depth_n)
cv2.imshow("laplacian", laplacian)
cv2.imshow("overlay with laplacian", overlay_laplacian)
cv2.imshow("overlay with depth heatmap", overlay_depth)
cv2.waitKey(0)

# save
# cv2.imwrite("/home/auv/depth_estimation/out/overlay.png", overlay)
# cv2.imwrite("/home/auv/depth_estimation/out/overlay2.png", overlay2)

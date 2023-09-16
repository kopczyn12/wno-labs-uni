import cv2
import os
import numpy as np

# specify the path to the folder containing images
folder_path = '/home/mkopcz/Desktop/uni/wno2/lab9/driver/'

file_list = []

for file_name in os.listdir(folder_path):
    if os.path.isfile(os.path.join(folder_path, file_name)):
        file_list.append(file_name)
print(file_list)

# loop through all files in the folder
for filename in os.listdir(folder_path):
    # check if the file is an image (ending with .jpg, .png, etc.)
    if filename.endswith('.jpg') or filename.endswith('.png'):
        # read the image file and append it to the list
        img = cv2.imread(os.path.join(folder_path, filename))
        # remove background using mask
        lower = np.array([215, 215, 215])
        upper = np.array([255, 255, 255])
        thresh = cv2.inRange(img, lower, upper)
        mask = 255 - thresh
        img_removed = cv2.bitwise_and(img, img, mask=mask)
        # find orientation of screwdriver handle using edge detection
        gray = cv2.cvtColor(img_removed, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))
                # calculate angle of rotation needed to flip the screwdriver handle downwards
                dx, dy = x2 - x1, y2 - y1
                angle = np.arctan2(dy, dx) * 180 / np.pi
                if angle > 90:
                    angle -= 180
                elif angle < -90:
                    angle += 180
                # rotate image
                rows, cols = img_removed.shape[:2]
                rotation_matrix = cv2.getRotationMatrix2D((cols/2, rows/2), -angle, 1)
                rotated_img = cv2.warpAffine(img_removed, rotation_matrix, (cols, rows))
                # save rotated image with filename starting with 'rotated_'
                cv2.imwrite(os.path.join(folder_path, f"rotated_{filename}"), rotated_img)
        else:
            # if no lines are detected, rotate the image by 180 degrees
            rows, cols = img_removed.shape[:2]
            rotation_matrix = cv2.getRotationMatrix2D((cols/2, rows/2), 180, 1)
            rotated_img = cv2.warpAffine(img_removed, rotation_matrix, (cols, rows))
            # save rotated image with filename starting with 'rotated_'
            cv2.imwrite(os.path.join(folder_path, f"rotated_{filename}"), rotated_img)

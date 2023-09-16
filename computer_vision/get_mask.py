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
        # read the image file and extract the mask
        img = cv2.imread(os.path.join(folder_path, filename))
        lower = np.array([215, 215, 215])
        upper = np.array([255, 255, 255])
        thresh = cv2.inRange(img, lower, upper)
        mask = 255 - thresh
        img_removed = cv2.bitwise_and(img, img, mask=mask)
        # resize the mask to 200x200 and save it
        resized_mask = cv2.resize(mask, (200, 200))
        cv2.imwrite(os.path.join(folder_path, f"mask_{filename}"), resized_mask)

import cv2
import os
import numpy as np
import io
from PIL import Image

# specify the path to the folder containing images
folder_path = '/home/mkopcz/Desktop/uni/wno2/lab9/driver/'

file_list = []

for file_name in os.listdir(folder_path):
    if os.path.isfile(os.path.join(folder_path, file_name)):
        file_list.append(file_name)
print(file_list)
# initialize an empty list to store the images
image_list = []

# loop through all files in the folder
for filename in os.listdir(folder_path):
    # check if the file is an image (ending with .jpg, .png, etc.)
    if filename.endswith('.jpg') or filename.endswith('.png'):
        # read the image file and append it to the list
        image = cv2.imread(os.path.join(folder_path, filename))
        image_list.append(image)

# for photo in image_list:
#     cv2.imshow(f'Image', photo)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

for i in range(len(file_list)):
    
    img = cv2.imread(folder_path + file_list[i])
    lower = np.array([215, 215, 215])
    upper = np.array([255, 255, 255])

    thresh = cv2.inRange(img, lower, upper)
    mask = 255 - thresh
    img_removed = cv2.bitwise_and(img, img, mask=mask)
    cv2.imwrite(f"output{i}.jpg", img_removed)

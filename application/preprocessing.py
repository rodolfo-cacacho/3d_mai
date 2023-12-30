import cv2
import numpy as np
import os
from os import walk
import imutils

#def calculate_cropping_indices(img_shape):
#    real_aspect_ratio = img_shape[0] / img_shape[1]
#    goal_x = (9/16) * img_shape[1]
#    x_mid = img_shape[0] / 2
#    new_x_start = int(x_mid - (goal_x/2))
#    new_x_end = int(x_mid + (goal_x/2))
#    return new_x_start, new_x_end

def preprocess_images(SOURCE_IMAGES_PATH, DESTINATION_IMAGES_PATH, TARGET_RESOLUTION=(800,450)): 
    """Find Contours and resize images (to 16:9). Store the preprocessed imagees in DESTINATION_IMAGES_PATH.

    Example usage: \n
    target_resolution = (800, 450) \n
    SOURCE_IMAGES_PATH = "" \n
    DESTINATION_IMAGES_PATH = "" \n
    preprocess_cad_images(SOURCE_IMAGES_PATH, DESTINATION_IMAGES_PATH, target_resolution)
    """
    
    subdir = [x[0] for x in os.walk(SOURCE_IMAGES_PATH)][0]
    files = os.walk(subdir).__next__()[2]
    if (len(files) > 0):
        for file in files:
            file_name = file.split(".")[0]
            image_name = os.path.join(subdir, file)
            if image_name[-4:] != ".png":
                print("Only .png files are allowed.")
                break
        
            img = cv2.imread(image_name)

            # Check if image is already 16:9. If not throw Exception.
            if img.shape[1] / img.shape[0] != 16/9:
                print("Image not 16:9!")
                raise Exception("Image not 16:9!")

            # Detect the contours
            gray = cv2.bilateralFilter(img, 3, 5, 5)
            edged = cv2.Canny(gray, 100, 200)
            cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            img = cv2.cvtColor(edged, cv2.COLOR_GRAY2BGR)  #add this line
            img = cv2.drawContours(img, cnts, -1, 255, 1)
            #im_bw = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]

            # Somehow I'm not allowed to remove the last dimension. Stick with 3 dimensions for now...
            img = img[:,:,0]
            img = np.dstack((img, img, img))

            # Calculate how much to crop to get from IPhone resolution to 16:9 aspect ratio
            # TODO:
            #if img.shape[0] / img.shape[1] != 16/9:
                #new_x_start, new_x_end = calculate_cropping_indices(img.shape)
                #img = img[new_x_start:new_x_end, :]

            # resize the image to a fixed size. Resize AFTER detecting the edges
            img = cv2.resize(img, TARGET_RESOLUTION) # 800 x 450 = ratio of 1920 x 1080 downscaled
        
            SAVING_PATH = os.path.join(DESTINATION_IMAGES_PATH, file)
            # Save preprocessed real image to folder
            cv2.imwrite(SAVING_PATH, img)

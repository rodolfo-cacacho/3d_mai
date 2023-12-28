import cv2
import os
import numpy as np

def create_label_files(images_path, labels_path, class_list):
    """Creates Label files to images. Stores labels in labels_path in YOLOv8 format.
    Also handles class names/labels.
    Returns populated class_list. \n

    Note: This will only be used for detectin bbox for the single_parts folder, since assemblies are annotated manually. \n

    Example usage: \n
    images_path = '/home/jetracer/Documents/3d_mai/application/test/single-parts/images' \n
    labels_path = '/home/jetracer/Documents/3d_mai/application/test/single-parts/labels' \n
    class_list = [] \n
    create_label_files(images_path, labels_path, class_list)
    """
    for part in os.listdir(images_path):

        # Handle class name/label
        # Note: class_list is empty most likely, since this is the first time creating label files.
        class_name = part.split("_x")[0]
        if class_name not in class_list:
            class_list.append(class_name)
        label = class_list.index(class_name)    

        # Get Image path
        full_path = os.path.join(images_path, part)  

        # Load the image
        image = cv2.imread(full_path)

        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Perform edge detection
        edges = cv2.Canny(blurred, 50, 150)

        # Find contours in the edge-detected image
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the convex hull of the contours
        convex_hull = cv2.convexHull(np.vstack(contours))

        # Calculate the bounding box of the convex hull
        x, y, w, h = cv2.boundingRect(convex_hull)

        # Calculate relative bounding box coordinates
        x1 = x
        y1 = y
        x2 = x + w
        y2 = y + h
        center_x = x1 + (x2 - x1) / 2
        center_y = y1 + (y2 - y1) / 2
        relative_width = (x2 - x1) / image.shape[1]
        relative_height = (y2 - y1) / image.shape[0]
        relative_center_x= center_x / image.shape[1]
        relative_center_y= center_y / image.shape[0]

        # Store label file
        filename = part.replace(".png", ".txt")
        filename = filename.replace(".jpg", ".txt")
        save_path = os.path.join(labels_path, filename)
        with open(save_path, 'w') as file:
            file.write(f"{label} {relative_center_x:.5f} {relative_center_y:.5f} {relative_width:.5f} {relative_height:.5f}")
            
    print("Detecting bounding boxes for single parts done.")
    print("class_list:", class_list)
    return class_list

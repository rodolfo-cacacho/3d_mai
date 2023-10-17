import cv2
import os
import numpy as np

path = './old_structure/Screenshots/Real_parts'
label = -1

for part in os.listdir(path):
    if part[0] != ".":
        label += 1
        for screenshot in os.listdir(path+'/'+part):
            if screenshot[0] != ".":
                # Load the image
                image = cv2.imread(path+'/'+part+'/'+screenshot)

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

                # Create a copy of the image for drawing the bounding box
                result_image = image.copy()

                # Calculate the bounding box of the convex hull
                x, y, w, h = cv2.boundingRect(convex_hull)

                # Draw the bounding box on the result image
                cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                x1 = x
                y1 = y
                x2 = x + w
                y2 = y + h

                center_x = x1 + (x2 - x1) / 2
                center_y = y1 + (y2 - y1) / 2
                relative_width = (x2 - x1) / image.shape[1]
                #print(relative_width)
                relative_height = (y2 - y1) / image.shape[0]
                #print(relative_height)
                relative_center_x= center_x / image.shape[1]
                relative_center_y= center_y / image.shape[0]
                #print(f"Bounding Box: (x1, y1, x2, y2) = ({x1}, {y1}, {x2}, {y2})")
                #print(f"Bounding Box: Center ({center_x:.5f}, {center_y:.5f}), Width {relative_width:.5f}, Height {relative_height:.5f}")
                #print(f"Bounding Box: Relative Center ({relative_center_x:.5f}, {relative_center_y:.5f}), Width {relative_width:.5f}, Height {relative_height:.5f}")

                filename = screenshot.replace("test", part+"|")
                filename = filename.replace(".jpg", "")
                images_path = 'data/train/images/'
                labels_path = 'data/train/labels/'
                images_bounded_path = 'data/framed/'

                # Open a file for writing the results
                with open(labels_path + filename + '.txt', 'w') as file:
                    file.write(f"{label},{relative_center_x:.5f},{relative_center_y:.5f},{relative_width:.5f},{relative_height:.5f}")

                # Save the result image
                cv2.imwrite(images_bounded_path + filename + '.jpg', result_image)

                # Save the original image
                cv2.imwrite(images_path + filename + '.jpg', image)
                
        

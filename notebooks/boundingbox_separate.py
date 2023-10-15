import cv2
import os

path = './old_structure/Screenshots/Real_parts'

for part in os.listdir(path):
    if part[0] != ".":
        for screenshot in os.listdir(path+'/'+part):
            if screenshot[0] != ".":
                # Load the image
                image = cv2.imread(path+'/'+part+'/'+screenshot)

                print(path+'/'+part+'/'+screenshot)

                # Convert the image to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # Apply Gaussian blur to reduce noise
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)

                # Perform edge detection
                edges = cv2.Canny(blurred, 50, 150)

                # Find contours in the edge-detected image
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Create a copy of the image for drawing bounding boxes
                result_image = image.copy()
                height, width = image.shape[:2]
                print(height, width)

                # List to store bounding box coordinates
                bounding_box = []

                # Iterate over the detected contours and draw bounding boxes
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    bounding_box.append((x, y, x + w, y + h))  # Store the coordinates
                    cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Print the original and modified bounding box coordinates
                for i, (x1, y1, x2, y2) in enumerate(bounding_box):
                    center_x = x1 + (x2 - x1) / 2
                    center_y = y1 + (y2 - y1) / 2
                    relative_width = (x2 - x1) / image.shape[1]
                    print(relative_width)
                    relative_height = (y2 - y1) / image.shape[0]
                    print(relative_height)
                    relative_center_x= center_x / image.shape[1]
                    relative_center_y= center_y / image.shape[0]
                    print(f"Bounding Box {i + 1}: (x1, y1, x2, y2) = ({x1}, {y1}, {x2}, {y2})")
                    print(f"Bounding Box {i + 1}: Center ({center_x:.5f}, {center_y:.5f}), Width {relative_width:.5f}, Height {relative_height:.5f}")
                    print(f"Bounding Box {i + 1}: Relative Center ({relative_center_x:.5f}, {relative_center_y:.5f}), Width {relative_width:.5f}, Height {relative_height:.5f}")
                
                # Save the result image
                cv2.imwrite('result_image.jpg', result_image)

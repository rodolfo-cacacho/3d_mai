import numpy as np
import os
from PIL import Image
import cv2

def get_files_in_subdirectories(folder_path, file_extension='', file_contains=''):
    """Returns a list of all files in the folder_path directory and its subdirectories."""
    files = []
    for root, directories, filenames in os.walk(folder_path):
        for filename in filenames:
            if file_extension == '' and file_contains == '':
                files.append(os.path.join(root, filename))
            elif file_extension != '' and file_contains == '':
                if filename.endswith(file_extension):
                    files.append(os.path.join(root, filename))
            elif file_extension == '' and file_contains != '':
                if file_contains in filename:
                    files.append(os.path.join(root, filename))
            else:
                if file_contains in filename and filename.endswith(file_extension):
                    files.append(os.path.join(root, filename))
    return files

def percentages_to_coordinates(bbox_percentages, image_width, image_height):
    """Converts relative bounding box coordinates to absolute pixel coordinates."""
    rx, ry, rwo, rho = bbox_percentages

    ho = rho*image_height
    wo = rwo*image_width
    # print(f'height o {ho} width {wo}')
    # print(f'height i {image_height} width {image_width}')

    x_1 = int((rx*image_width-wo/2.0))
    y_1 = int((ry*image_height-ho/2.0))
    x_2 = int((x_1 + wo))
    y_2 = int((y_1 + ho))

    return x_1, y_1, x_2, y_2

def coordinates_to_percentage(bbox_coordinates, image_width, image_height):
    """Converts absolute pixel coordinates to relative bounding box coordinates."""
    x1,y1,x2,y2 = bbox_coordinates

    wo = x2-x1
    ho = y2-y1

    rxo = round((x1 + wo/2.0)/image_width,4)
    ryo = round((y1 + ho/2.0)/image_height,4)
    rwo = round(wo/image_width,4)
    rho = round(ho/image_height,4)

    return rxo,ryo,rwo,rho

def append_text_files(file1_path, file2_path):
    """Appends the content of the second file to the first file."""
    try:
        # Read the content of the second file
        with open(file2_path, 'r') as file2:
            content_to_append = '\n'+file2.read()

        # Append the content to the first file
        with open(file1_path, 'a') as file1:
            file1.write(content_to_append)

    except FileNotFoundError:
        print(f"File not found: {file2_path}")


def resize_and_place_object(image_path, original_bbox, scale_factor,future_path):

    # Crop the region inside the original bounding box
    x1, y1, x2, y2 = original_bbox
    ow = x2-x1
    oh = y2-y1
    # print(f'{y1} {y2} {x1} {x2}')
    w_reduce = 960
    h_reduce = 500

    original_image = cv2.imread(image_path)
    object_region = original_image[y1:y2, x1:x2].copy()
    new_w = int(scale_factor*(ow))
    new_h = int(scale_factor*(oh))
    if(scale_factor > 1 or scale_factor <1):
        resized_object = cv2.resize(object_region, (new_w,new_h))
    else:
        resized_object = object_region.copy()

    # print(f'h {new_h} w{new_w}')
    # Paste the object into the new random location
    original_image[y1:y2, x1:x2] = [255, 255, 255]

    print("new_w:", new_w)
    print("new_h:", new_h)

    # Calculate the maximum x and y coordinates for the new location
    max_x = original_image.shape[1] - new_w - int(w_reduce/2)
    max_y = original_image.shape[0] - new_h - int(h_reduce/2)

    # Generate random x and y coordinates for the new location
    x_start = int(w_reduce/2)
    x_end = x_start + max_x + 1
    y_start = int(h_reduce/2)
    y_end = y_start + max_y + 1
    print("x_start:", x_start)
    print("x_end:", x_end)
    print("y_start:", y_start)
    print("y_end:", y_end)

    new_x = np.random.randint(int(w_reduce/2), max_x + 1)
    new_y = np.random.randint(int(h_reduce/2), max_y + 1)
    original_image[new_y:new_y+new_h, new_x:new_x+new_w] = resized_object
    cv2.imwrite(future_path, original_image)

    image_path_save = future_path.replace('images','images_wbb')
    cv2.rectangle(original_image, (new_x, new_y), (new_w + new_x, new_h + new_y), (255, 0, 0), 2)
    cv2.imwrite(image_path_save, original_image)

    new_coords = [new_x,new_y]
    new_bbox = [new_x,new_y,new_w + new_x, new_h + new_y]

    return new_coords,new_bbox

def calculate_displaced_bbox(old_bbox,old_cords,new_cords,scale_factor,image_path):
    """Calculates the new bounding box for the object in the image."""
    x1,y1,x2,y2 = old_bbox
    w = x2 - x1
    h = y2 - y1
    ox = old_cords[0]
    oy = old_cords[1]

    nx = new_cords[0]
    ny = new_cords[1]

    dist_vert_x = (x1 - ox)*scale_factor
    dist_vert_y = (y1 - oy)*scale_factor

    vert_x = nx + dist_vert_x
    vert_y = ny + dist_vert_y

    end_x = vert_x + w*scale_factor
    end_y = vert_y + h*scale_factor

    displaced_bbox = [vert_x,vert_y,end_x,end_y]
    displaced_bbox = [int(x) for x in displaced_bbox]
    
    #image_path_save = image_path.replace('images','images_wbb')
    #original_image = cv2.imread(image_path_save)
    #cv2.rectangle(original_image, (int(vert_x), int(vert_y)), (int(end_x),int(end_y)), (0, 0, 255), 2)
    #cv2.imwrite(image_path_save, original_image)

    return displaced_bbox


def move_and_zoom(input_folder, output_folder, CLASS_LIST):
    """Moves and zooms the objects in the images in the input folder and saves the results in the output folder.
    Note: Also append new classes to the CLASS_LIST here!"""
    IMAGE_FILE_EXTENSION = '.jpg'
    TEXT_FILE_EXTENSION = '.txt'
    FILENAME_CLASS_SEPARATOR = '_ '

    input_folder_images = os.path.join(input_folder, 'images')
    input_folder_labels = os.path.join(input_folder, 'labels')

    output_folder_images = os.path.join(output_folder, 'images')
    output_folder_labels = os.path.join(output_folder, 'labels')
    print("outputfolder_l 1:", output_folder_labels)

    images_move = get_files_in_subdirectories(input_folder_images, IMAGE_FILE_EXTENSION)

    zoom_range = [1,0.69,0.52]
    zoom_names = ['z1oom','z2oom','z3oom']

    for index_1,full_path in enumerate(images_move):
        # Handle class name and file path
        print(full_path)
        filename = full_path.split('/')[-1]
        classname = filename.split(FILENAME_CLASS_SEPARATOR)[1] # TODO: Watch out here. Should be 0 normally.
        print(classname)
        if classname not in CLASS_LIST:
            CLASS_LIST.append(classname)
            print(f'appended new class {classname}')
        
        # TODO: Do I need this?
        source_label_path = full_path.replace('images','labels').replace(IMAGE_FILE_EXTENSION, TEXT_FILE_EXTENSION)
        destination_label_path = os.path.join(output_folder_labels, filename.replace(IMAGE_FILE_EXTENSION, TEXT_FILE_EXTENSION))
        append_text_files(source_label_path, destination_label_path)

        # Get width and height of image
        original_image = Image.open(full_path)
        w,h = original_image.size

        # Read the content of the label file and split it into lines
        with open(source_label_path, 'r') as file:
            lines = file.read().splitlines()

        # Convert each line to a list of floats
        bounding_boxes = [list(map(float, line.split())) for line in lines] # Labels

        # Iterate over zoom range
        for index_zoom, zoom in enumerate(zoom_range):

            result_bounding_boxes = []
            # Iterate over each of the bounding boxes
            for index_bbox,bbox_l in enumerate(bounding_boxes):
                bbox_per = bbox_l[1:5]
                bbox_per = [round(element,4) for element in bbox_per]

                # TODO: Do I need this? What is this?
                #object_name = names[int(bbox_l[0])]
                #object = mapping_dict[object_name]
                
                bbox = percentages_to_coordinates(bbox_per,w,h)
                # Zoom and move image
                if(index_bbox == 0):
                    # If it's the first bounding box - also move the object in the image.
                    input_path = full_path
                    output_path = os.path.join(output_folder, "images", filename)
                    new_position, new_bbox = resize_and_place_object(input_path, bbox, zoom, output_path)
                    new_bbox_l = [classname, new_bbox]
                    result_bounding_boxes.append(new_bbox_l)
                    old_cords = [bbox[0],bbox[1]]

                # Calculate new bounding boxes
                else:
                    # If it's not the first bounding box - only calculate the new bounding box - since the object is already moved.
                    wbb_save_path = "NOT_IMPORTANT"
                    new_bbox = calculate_displaced_bbox(bbox, old_cords, new_position, zoom, wbb_save_path)
                    new_bbox_l = [classname,new_bbox]
                    result_bounding_boxes.append(new_bbox_l)

            print("outputfolder_l:", output_folder_labels)
            labels_path = os.path.join(output_folder_labels, filename.replace(IMAGE_FILE_EXTENSION, TEXT_FILE_EXTENSION).replace(zoom_names[0],zoom_names[index_zoom]))
            with open(labels_path, 'w') as output_file:
                for index,item in enumerate(result_bounding_boxes):
                    object = item[0]
                    bbox = coordinates_to_percentage(item[1],1920,1080)
                    if(index == len(result_bounding_boxes)-1):
                        line = f"{object} {bbox[0]:.5f} {bbox[1]:.5f} {bbox[2]:.5f} {bbox[3]:.5f}"
                    else:
                        line = f"{object} {bbox[0]:.5f} {bbox[1]:.5f} {bbox[2]:.5f} {bbox[3]:.5f}\n"
                    output_file.write(line)
    return CLASS_LIST

#input_folder = "/home/jetracer/Documents/3d_mai/application/test/combined-annotated"
#output_folder = "/home/jetracer/Documents/3d_mai/application/test/train"
#resulting_class_list = move_and_zoom(input_folder, output_folder, ["assembly"])
#print("resulting_class_list:", resulting_class_list)    


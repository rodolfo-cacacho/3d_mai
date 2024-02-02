import cv2
import os
import numpy as np
import yaml
from PIL import Image


def append_text_files(file1_path, file2_path,names,map_dict):
    try:
        # Read the content of the second file
        with open(file2_path, 'r') as file:
            lines = file.read().splitlines()
        bounding_boxes = [list(map(float, line.split())) for line in lines] # Labels
        for n,i in enumerate(bounding_boxes):
            object = names[int(i[0])]
            new_idx = map_dict[object]
            bounding_boxes[n][0] = new_idx
        content_to_append = '\n'
        for index,item in enumerate(bounding_boxes):
            if(index == len(bounding_boxes)-1):
                line = f"{item[0]} {item[1]:.8f} {item[2]:.8f} {item[3]:.8f} {item[4]:.8f}"
            else:
                line = f"{item[0]} {item[1]:.8f} {item[2]:.8f} {item[3]:.8f} {item[4]:.8f}\n"
            content_to_append = content_to_append+line
        
        # Append the content to the first file
        with open(file1_path, 'a') as file1:
            file1.write(content_to_append)

    except FileNotFoundError:
        print(f"File not found: {file2_path}")


def coordinates_to_percentage(bbox_coordinates, image_width, image_height):
    x1,y1,x2,y2 = bbox_coordinates

    wo = x2-x1
    ho = y2-y1

    rxo = round((x1 + wo/2.0)/image_width,4)
    ryo = round((y1 + ho/2.0)/image_height,4)
    rwo = round(wo/image_width,4)
    rho = round(ho/image_height,4)

    return rxo,ryo,rwo,rho

def percentages_to_coordinates(bbox_percentages, image_width, image_height):
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


def resize_and_place_object(image_path, original_bbox, scale_factor,future_path,bbox_path):

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

    # Calculate the maximum x and y coordinates for the new location
    max_x = original_image.shape[1] - new_w - int(w_reduce/2)
    max_y = original_image.shape[0] - new_h - int(h_reduce/2)

    # Generate random x and y coordinates for the new location
    new_x = np.random.randint(int(w_reduce/2), max_x + 1)
    new_y = np.random.randint(int(h_reduce/2), max_y + 1)
    original_image[new_y:new_y+new_h, new_x:new_x+new_w] = resized_object
    cv2.imwrite(future_path, original_image)

    image_path_save = bbox_path
    cv2.rectangle(original_image, (new_x, new_y), (new_w + new_x, new_h + new_y), (255, 0, 0), 2)
    cv2.imwrite(image_path_save, original_image)

    new_coords = [new_x,new_y]
    new_bbox = [new_x,new_y,new_w + new_x, new_h + new_y]

    return new_coords,new_bbox

def calculate_displaced_bbox(old_bbox,old_cords,new_cords,scale_factor,image_path):

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
    
    image_path_save = image_path
    original_image = cv2.imread(image_path_save)
    cv2.rectangle(original_image, (int(vert_x), int(vert_y)), (int(end_x),int(end_y)), (0, 0, 255), 2)
    cv2.imwrite(image_path_save, original_image)

    return displaced_bbox

def create_label_files(images_path, labels_path, class_list,assembly_list,bbox_path):
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
    # print(f'classes: {class_list} \n assemblies: {assembly_list}')
    for part in os.listdir(images_path):
        # Handle class name/label
        # Note: class_list is empty most likely, since this is the first time creating label files.
        class_name = part.split("_x")[0]
        if class_name not in class_list:
            class_list.append(class_name)
        label = class_list.index(class_name)    

        # Get Image path
        full_path = os.path.join(images_path, part)  

        # print(f'reading image {part} \n class {class_name} \n path {full_path}')

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

        # Create a copy of the image for drawing the bounding box
        result_image = image.copy()

        # Calculate the bounding box of the convex hull
        x, y, w, h = cv2.boundingRect(convex_hull)

        image_width = image.shape[1]
        image_height = image.shape[0]

        aratio = w/h
        if aratio >= 1:
            px = 1
            py = int(1*aratio)
        else:
            px = int(1.0/aratio)
            py = 1
        x1 = x-px
        y1 = y-py
        x2 = x + w + px
        y2 = y + h + py
        wn = x2-x1
        hn = y2-y1
        w_reduce = 960
        h_reduce = 500
        # Calculate the maximum x and y coordinates for the new location
        max_x = image_width - w - int(w_reduce/2)
        max_y = image_height - h - int(h_reduce/2)

        # Generate random x and y coordinates for the new location
        new_x = np.random.randint(int(w_reduce/2), max_x + 1)
        new_y = np.random.randint(int(h_reduce/2), max_y + 1)
        if(class_name in assembly_list):
            new_x = x1
            new_y = y1
            images_path_save = images_path
            labels_path_save = labels_path
        else:
            images_path_save = images_path.replace('single-parts','combined-annotated')
            labels_path_save = labels_path.replace('single-parts','combined-annotated')

        # Extract the object
        object_region = image[y1:y2, x1:x2].copy()

        # Paste the object into the new random location
        image[y1:y2, x1:x2] = [255, 255, 255]
        image[new_y:new_y+hn, new_x:new_x+wn] = object_region

        img_saving_path = os.path.join(images_path_save,part)
        if(class_name not in assembly_list):
            cv2.imwrite(img_saving_path, image)
            # Draw the bounding box on the result image
            cv2.rectangle(image, (new_x, new_y), (new_x + wn, new_y + hn), (0, 255, 0), 2)
            bounding_box_saving_path = os.path.join(bbox_path,'single-parts',part)
            cv2.imwrite(bounding_box_saving_path, image)

        bbox_cord = [new_x,new_y,new_x+wn,new_y+hn]

        relative_center_x, relative_center_y, relative_width, relative_height = coordinates_to_percentage(bbox_cord,image_width,image_height)

        # Store label file
        filename = part.replace(".png", ".txt")
        filename = filename.replace(".jpg", ".txt")
        save_path = os.path.join(labels_path_save, filename)
        with open(save_path, 'w') as file:
            file.write(f"{label} {relative_center_x:.5f} {relative_center_y:.5f} {relative_width:.5f} {relative_height:.5f}")
            
    return class_list

def combine_move_zoom(assemblies_path,result_path,bbox_path,class_list,assembly_list):

    # print(f'classes: {class_list} \n assemblies: {assembly_list}')
    path_config = os.path.join(assemblies_path,'data.yaml')

    # Load YAML file
    with open(path_config, 'r') as file:
        data = yaml.safe_load(file)
    
    names = data.get('names', [])

    zoom_range = [1,0.69,0.52]
    zoom_names = ['z1oom','z2oom','z3oom']

    # Create a mapping dictionary for the first list
    mapping_dict = {value: index for index, value in enumerate(class_list)}

    images_path = os.path.join(assemblies_path,'images')
    images_ = os.listdir(images_path)
    labels_path = os.path.join(assemblies_path,'labels')
    labels_rb_path = os.path.join(assemblies_path,'labels_rb')
    bbox_path = os.path.join(bbox_path,'assemblies')

    for part in images_:
        # Handle class name/label
        # Note: class_list is empty most likely, since this is the first time creating label files.
        class_name = part.split("_x")[0]
        if class_name not in class_list:
            class_list.append(class_name)
        label = class_list.index(class_name) 
        label_1 = os.path.join(labels_path,part).replace('png','txt')
        label_2 = os.path.join(labels_rb_path,part).replace('png','txt')
        append_text_files(label_1, label_2,names,mapping_dict)
        image_file = os.path.join(images_path,part)
        original_image = Image.open(image_file)
    
        w,h = original_image.size
        del(original_image)
        # Read the content of the file and split it into lines
        with open(label_1, 'r') as file:
            lines = file.read().splitlines()

        # Convert each line to a list of floats
        bounding_boxes = [list(map(float, line.split())) for line in lines] # Labels

        for index_zoom, zoom in enumerate(zoom_range):

            result_bounding_boxes = []
            for index_bbox,bbox_l in enumerate(bounding_boxes):
                bbox_per = bbox_l[1:5]
                bbox_per = [round(element,4) for element in bbox_per]
                object_name = class_list[int(bbox_l[0])]
                object = mapping_dict[object_name]
                bbox = percentages_to_coordinates(bbox_per,w,h)
                # print(f'zoom: {zoom}x bbox {object_name} : bbox {bbox}')
                part_file = part.replace(zoom_names[0],zoom_names[index_zoom])
                save_path_i_bb = os.path.join(bbox_path,part_file)
                # image_file = image.replace(zoom_names[0],zoom_names[index_zoom])
                save_path_i = os.path.join(result_path,'images',part_file)
                # print(f'Saving path: {save_path_i}')

                # Zoom and move image
                if(index_bbox == 0):
                    new_position,new_bbox = resize_and_place_object(image_file, bbox, zoom,save_path_i,save_path_i_bb)
                    new_bbox_l = [object, new_bbox]
                    result_bounding_boxes.append(new_bbox_l)
                    old_cords = [bbox[0],bbox[1]]
                # Calculate new bounding boxes
                else:
                    new_bbox = calculate_displaced_bbox(bbox,old_cords,new_position,zoom,save_path_i_bb)
                    new_bbox_l = [object,new_bbox]
                    result_bounding_boxes.append(new_bbox_l)

            # print(f'result bbox{result_bounding_boxes}')
            label_file = part_file.replace('png','txt')
            labels_path_f = os.path.join(result_path,'labels',label_file)
            with open(labels_path_f, 'w') as output_file:
                for index,item in enumerate(result_bounding_boxes):
                    object = item[0]
                    bbox = coordinates_to_percentage(item[1],1920,1080)
                    if(index == len(result_bounding_boxes)-1):
                        line = f"{object} {bbox[0]:.5f} {bbox[1]:.5f} {bbox[2]:.5f} {bbox[3]:.5f}"
                    else:
                        line = f"{object} {bbox[0]:.5f} {bbox[1]:.5f} {bbox[2]:.5f} {bbox[3]:.5f}\n"
                    output_file.write(line)

    return class_list

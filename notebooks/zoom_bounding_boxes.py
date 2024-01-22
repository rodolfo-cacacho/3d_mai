import numpy as np
import copy
import os
import re
import random
from PIL import Image
import cv2
import yaml
from matplotlib import pyplot as plt


def get_subdirectories(folder_path):
    subdirectories = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            subdirectories.append(item)
    return subdirectories

def get_files_in_subdirectories(folder_path, file_extension='', file_contains=''):
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


def extract_string(filename,format = 'stl'):
    pattern = r'\/([^/]+)\.'+format+'$'
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    else:
        return None
    
# Defining a function to convert degrees to radians.
def deg2rad(deg):
    return deg * np.pi/180

def get_rotated_pcd(pcd, x_theta, y_theta, z_theta):
    pcd_rotated = copy.deepcopy(pcd)
    R = pcd_rotated.get_rotation_matrix_from_axis_angle([x_theta, y_theta, z_theta])
    pcd_rotated.rotate(R, center=(0, 0, 0))
    return pcd_rotated

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")
        return False
    else:
        print(f"Folder already exists: {folder_path}")
        return True

def delete_file(file_path):
    try:
        os.remove(file_path)
        # print(f"File '{file_path}' deleted successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except PermissionError:
        print(f"Permission denied: unable to delete file '{file_path}'.")
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")

def create_binary_list(n, percentage_of_ones):
    if percentage_of_ones < 0 or percentage_of_ones > 100:
        raise ValueError("Percentage_of_ones must be between 0 and 100")

    num_ones = int(n * (percentage_of_ones / 100))
    num_zeros = n - num_ones

    binary_list = [1] * num_ones + [0] * num_zeros
    random.shuffle(binary_list)

    return binary_list

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

def coordinates_to_percentage(bbox_coordinates, image_width, image_height):
    x1,y1,x2,y2 = bbox_coordinates

    wo = x2-x1
    ho = y2-y1

    rxo = round((x1 + wo/2.0)/image_width,4)
    ryo = round((y1 + ho/2.0)/image_height,4)
    rwo = round(wo/image_width,4)
    rho = round(ho/image_height,4)

    return rxo,ryo,rwo,rho

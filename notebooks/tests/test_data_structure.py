''' 
Tests on the data structure of training images.
YOLOv8 requires a specific data structure for training images:
    - train folder
        - images folder
            - image1.jpg
        - labels folder
            - image1.txt
    - val folder
        - images folder
            - image2.jpg
        - labels folder
            - image2.txt

This test checks if the data structure is correct.
'''

import os
import shutil
import cv2

from pathlib import Path

DATA_PATH = Path('../../data')

def check_data_structure(data_path):
    print("--- START: CHECKING FOLDER STRUCTURE FOR:", data_path)

    # Check if train and val folder exist
    check_train_val_structure(data_path)
    print()

    # Check if images and labels folder exist  
    check_folder_structure(data_path/'train')
    check_folder_structure(data_path/'val')
    print()

    # Check if images and labels are in the correct folder
    check_images_structure(data_path/'train')
    check_labels_structure(data_path/'val')
    print()

    # Check if names of images and labels are the same
    check_names_of_files(data_path/'train')
    check_names_of_files(data_path/'val')

    print("--- END: CHECKING FOLDER STRUCTURE FOR:", data_path)

def check_train_val_structure(data_path):
    # Check if subfolders exist
    assert os.path.isdir(data_path/'train')
    assert os.path.isdir(data_path/'val')
    print("checking train and val subfolders in:", data_path)

def check_folder_structure(data_path):
    # Check if subfolders exist
    assert os.path.isdir(data_path/'images')
    assert os.path.isdir(data_path/'labels')
    print("checked images and labels subfolders in:", data_path)

def check_images_structure(data_path):
    image = next((data_path/'images').glob('*'))
    assert image.suffix == '.jpg'
    print("checked image suffixes in:", data_path)

def check_labels_structure(data_path):
    label = next((data_path/'labels').glob('*'))
    assert label.suffix == '.txt'
    print("checked label suffixes in:", data_path)

def check_names_of_files(data_path):
    # Check if names of images and labels are the same
    images = [image.stem for image in (data_path/'images').glob('*')]
    labels = [label.stem for label in (data_path/'labels').glob('*')]

    # Check if images and labels are the same length
    try:
        assert len(images) == len(labels)
    except AssertionError:
        print("FAILED: Incorrect number of images and labels in:", data_path)

    # Iterate through all labels and check if there is a corresponding image
    for label in labels:
        try:
            assert label in images
        except AssertionError:
            print("FAILED:", label, "is missing in images in:", data_path)

    # Iterate through all images and check if there is a corresponding label
    for image in images:
        try:
            assert image in labels
        except AssertionError:
            print("FAILED:", image, "is missing in labels in:", data_path)

    print("checked names of files in:", data_path)


def check_image_dimensions(data_path):
    image = next((data_path).glob('*'))

    # Load image and check dimensions
    image = cv2.imread(str(image))

    # Assert that it's 2D images
    try:
        assert len(image.shape) == 3
        print("PASSED: image dimensions:", image.shape, "in:", data_path)
    except:
        print("FAILED: image is not 3D, image dimensions:", image.shape, "in:", data_path)


if __name__ == '__main__':
    # Check data folder structure
    check_data_structure(DATA_PATH)
    print()

    # Check if example image dimensions 
    print("--- START: CHECKING IMAGE DIMENSIONS")
    check_image_dimensions(DATA_PATH/'train'/'images')
    check_image_dimensions(DATA_PATH/'val'/'images')
    check_image_dimensions(DATA_PATH/'test'/'images')
    print("--- END: CHECKING IMAGE DIMENSIONS")

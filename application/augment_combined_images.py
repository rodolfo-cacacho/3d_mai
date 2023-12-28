import random
import shutil

def augment_combined_folder(folder_path, num_of_augmented_images=1):
    images_folder = os.path.join(folder_path, "images")
    labels_folder = os.path.join(folder_path, "labels")

    # Augment images in images folder
    files_paths = get_files_in_subdirectories(images_folder, file_extension=".png")
    for file_path in files_paths:
        #print("augmenting...:", file_path)
        for i in range(num_of_augmented_images):
            output_filepath = file_path # Since augmented images are added to copied original images.
            NOISE_STD = random.choice([45, 50, 55])
            output_filepath = output_filepath.replace(".", "_augmented_" + str(i+1) + ".")
            augment_image(file_path, output_filepath, noise_std=NOISE_STD)
    # TODO: Maybe: Shuffle the folder images
            
    # Update bboxes in labels folder
    update_labels_folder(labels_folder, num_of_augmented_images)
            
    # Remove original images and labels. Only keep augmented ones.
    delete_files_without_keyword(labels_folder, keyword="_augmented")
    delete_files_without_keyword(images_folder, keyword="_augmented")

    print("Augmenting (noise) combined images done.")

import os
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


import cv2
import numpy as np
import random
import matplotlib.pyplot as plt

def color_jitter(image, brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1):
    # Convert the image to the HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Adjust brightness
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + brightness), 0, 255)

    # Adjust contrast
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + contrast), 0, 255)

    # Adjust saturation
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + saturation), 0, 255)

    # Adjust hue
    hsv[:, :, 0] = (hsv[:, :, 0] + hue * 360) % 180

    # Convert the image back to BGR
    jittered_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return jittered_image

def apply_gaussian_blur(image, sigma=0.3):
    # Apply Gaussian blur
    blurred_image = cv2.GaussianBlur(image, (0, 0), sigma)

    return blurred_image

def apply_random_noise(image, mean=0, std=45):
    # Generate random noise
    noise = np.random.normal(mean, std, image.shape)

    # Add noise to the image
    noisy_image = np.clip(image + 0.25*noise, 0, 255).astype(np.uint8)

    return noisy_image

def augment_image(image_path, output_path, noise_std=45):
    # Read the original image
    image = cv2.imread(image_path)

    # Apply color jittering
    jittered_image = color_jitter(image)

    # Apply Gaussian blur
    blurred_image = apply_gaussian_blur(jittered_image)

    # Apply random noise
    noisy_image = apply_random_noise(blurred_image, mean=0, std=noise_std)

    # Save the augmented image
    cv2.imwrite(output_path, noisy_image)
        

def update_labels_folder(folder_path, num_of_augmented_images):
    # Duplicate all label files and add _augmented to the filename
    # List all files in the folder
    files = os.listdir(folder_path + "/")

    # Filter only TXT files
    txt_files = [file for file in files if file.lower().endswith(".txt")]

    # Duplicate and rename each TXT file
    for txt_file in txt_files:
        if "_augmented" in txt_file:
            print("Already run before!")
            break 
        
        original_path = os.path.join(folder_path, txt_file)

        for i in range(num_of_augmented_images):    
            # Create a new file name with "_augmented" suffix
            new_name, extension = os.path.splitext(txt_file)
            new_name += "_augmented_" + str(i+1) + extension

            # Create the new path
            new_path = os.path.join(folder_path, new_name)

            # Duplicate the TXT file
            shutil.copy(original_path, new_path)



# Remove images and label files without "_augmented" in the file name
def delete_files_without_keyword(folder_path, keyword="_augmented"):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Check if the keyword is not present in the file name
        if keyword not in filename:
            try:
                os.remove(file_path)
                #print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Error deleting {filename}: {e}")

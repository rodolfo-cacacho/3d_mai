import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import os
import shutil # For copying files
import subprocess # For opening folder in file explorer
import platform # For checking operating system
import yaml # For editing config.yaml file

def show_folder(folder_path):
        # Open the assembly folder, that the user should upload to Roboflow
        if platform.system() == "Windows":
            subprocess.run(["explorer", folder_path], shell=True)
        elif platform.system() == "Darwin":
            subprocess.run(["open", folder_path])
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", folder_path])
        else:
            print("Unsupported operating system") 

def copy_folder(source_folder, destination_folder):
    """For copying a folder to another folder
    Note: Make sure that the content in the destination folder is not overwritten. The content should just be appended.
    Note: This is important for multiple parts of the application. That's why it's a separate function.
    """
    # Check if the destination folder exists. Create otherwise.
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder, exist_ok=True)
        print(f"Created folder: {destination_folder}")

    # Specify folder paths
    source_images_folder = os.path.join(source_folder, "images")
    destination_images_folder = os.path.join(destination_folder, "images")
    source_labels_folder = os.path.join(source_folder, "labels")
    destination_labels_folder = os.path.join(destination_folder, "labels")

    # Go through source_folder images and labels folder -> Copy file by file to destination_folder images and labels folder    
    # Copy over images 
    source_images = os.listdir(source_images_folder)
    num_images = len(source_images)
    for file in source_images:
        source_file_path = os.path.join(source_images_folder, file)
        destination_file_path = os.path.join(destination_images_folder, file)
        try:
            shutil.copy(source_file_path, destination_file_path)
        except shutil.Error as e:
            print(f"Error copying file: {e}")
            num_images -= 1
        except Exception as e:
            print(f"Unexpected error: {e}")
            num_images -= 1
    print(f"Copyied all images from '{source_folder}' to '{destination_folder}' successfully.")

    # Copy over labels 
    source_labels = os.listdir(source_labels_folder)
    num_labels = len(source_labels)
    for file in source_labels:
        source_file_path = os.path.join(source_labels_folder, file)
        destination_file_path = os.path.join(destination_labels_folder, file)
        try:
            shutil.copy(source_file_path, destination_file_path)
        except shutil.Error as e:
            print(f"Error copying file: {e}")
            num_labels -= 1
        except Exception as e:
            print(f"Unexpected error: {e}")
            num_labels -= 1
    print(f"Copyied all labels from '{source_folder}' to '{destination_folder}' successfully.")
    
    return num_images, num_labels


"""For selecting folder where all the images and model should be stored on local machine

Creates the following folder structure:#
    - cad-files: For storing the 3D CAD files
    - assembly-images: For storing the assembly images that the user has to manually annotate
    - original-images: For storing all annotated images (assemblies and single parts)
    - preprocessed: For storing all preprocessed images
    - train: TODO
"""
class Window0:
    def __init__(self, root, next_callback=None):
        self.root = root
        self.title = "Assembly detection"

        # Select folder for storing everything
        welcome_label = tk.Label(root, text="Select folder where to store everything about this model (Images, model, ...).")
        welcome_label.pack(pady=10)

        # Show selected folder
        self.folder_path_label = tk.Label(root, text="Selected folder:" + FOLDER_PATH)
        self.folder_path_label.pack(pady=10)

        # Finished Uploading Button
        upload_button = tk.Button(root, text="Select folder", command=self.select_folder)
        upload_button.pack(side=tk.TOP, pady=5)

        # Next Button
        finish_button = tk.Button(root, text="Next step", command=self.next)
        finish_button.pack(side=tk.TOP, pady=5)

        # Callback for Next Window
        self.next_callback = next_callback

    def select_folder(self):
        # Open the native file dialog for selecting a folder
        folder_path = filedialog.askdirectory(title="Select Folder")

        # Update the selected folder path variable
        global FOLDER_PATH
        FOLDER_PATH = folder_path

        # Update label
        self.folder_path_label.config(text="Selected folder:" + FOLDER_PATH)

    def next(self):
        self.create_folder_structure()

        # Call the callback function if provided
        if self.next_callback:
            self.destroy()  # Destroy the widgets of the current window
            self.next_callback()   # Show the next window

    def create_folder_structure(self):
        folders = [
            "cad-files", 
            "assembly-images", # Only images
            "single-parts", "single-parts/images", "single-parts/labels", 
            "combined-annotated", "combined-annotated/images", "combined-annotated/labels", 
            "preprocessed", "preprocessed/images", "preprocessed/labels",
            "test", "test/images", "test/predictions",
        ]

        for folder in folders:
            folder_path = os.path.join(FOLDER_PATH, folder)

            # Check if the folder exists
            if os.path.exists(folder_path):
                # List files in the folder
                files = os.listdir(folder_path)

                if files:
                    print(f"There are files in {folder_path}")

                    # Ask for confirmation using a Tkinter popup
                    confirmation = messagebox.askyesno("Confirmation", f"Do you want to delete all files in {folder_path}?")

                    if confirmation:
                        # Delete all files in the folder
                        for file in files:
                            file_path = os.path.join(folder_path, file)
                            os.remove(file_path)
                        print(f"All files in {folder_path} deleted.")
            else:
                os.makedirs(folder_path, exist_ok=True)
                print(f"{folder_path} created.")
        

    def destroy(self):
        # Destroy all widgets in the current window
        for widget in self.root.winfo_children():
            widget.destroy()


"""For uploading assemblies and single parts
"""
class Window1:
    def __init__(self, root, next_callback=None):
        self.root = root
        self.title = "Assembly detection"
        global assemblies
        global single_parts

        # Welcome Text
        welcome_label = tk.Label(root, text="Upload 3D CAD objects. Assemblies and single parts.")
        welcome_label.pack(pady=10)

        # Assemblies Upload List
        assemblies_uploaded_label = tk.Label(root, text="Assemblies uploaded")
        assemblies_uploaded_label.pack(pady=[10, 0])
        self.assemblies_uploaded = tk.Listbox(root, selectmode=tk.MULTIPLE, width=40, height=10, borderwidth=2, relief="solid")
        self.assemblies_uploaded.pack(pady=0)
        upload_button = tk.Button(root, text="Upload assemblies", command=self.upload_assemblies)
        upload_button.pack(side=tk.TOP, pady=5)

        # Single parts Upload List
        single_parts_uploaded_label = tk.Label(root, text="Single parts uploaded")
        single_parts_uploaded_label.pack(pady=[10, 0])
        self.single_parts_uploaded = tk.Listbox(root, selectmode=tk.MULTIPLE, width=40, height=10, borderwidth=2, relief="solid")
        self.single_parts_uploaded.pack(pady=0)
        single_parts_upload_button = tk.Button(root, text="Upload single parts", command=self.upload_single_parts)
        single_parts_upload_button.pack(side=tk.TOP, pady=5)

        # Finished Uploading Button
        finish_button = tk.Button(root, text="Next step", command=self.create_images)
        finish_button.pack(side=tk.TOP, pady=5)

        # File Types for Upload
        self.file_types = ("3D CAD parts", "stl")

        # Callback for Next Window
        self.next_callback = next_callback

    def upload_assemblies(self):
        # Open the native file dialog for uploading files
        file_paths = filedialog.askopenfilenames(title=f"Select {self.file_types} files", filetypes=[(self.file_types[0], f"*.{self.file_types[1].lower()}")])
        if file_paths:
            # Clear existing items in the list
            self.assemblies_uploaded.delete(0, tk.END)

            # Display selected file names in the list
            for file_path in file_paths:
                file_name = file_path.split("/")[-1]
                self.assemblies_uploaded.insert(tk.END, file_name)
                assemblies.append(file_path)

    def upload_single_parts(self):
        # Open the native file dialog for uploading files
        file_paths = filedialog.askopenfilenames(title=f"Select {self.file_types} files", filetypes=[(self.file_types[0], f"*.{self.file_types[1].lower()}")])
        if file_paths:
            # Clear existing items in the list
            self.single_parts_uploaded.delete(0, tk.END)

            # Display selected file names in the list
            for file_path in file_paths:
                # Add the file path to the list
                file_name = file_path.split("/")[-1]
                self.single_parts_uploaded.insert(tk.END, file_name)
                single_parts.append(file_path)

    """Creating images from 3D CAD files.
    """
    def create_images(self):
        # TODO: Create 2D screenshots from stl files.
        print("Creating images from 3D CAD files...")
        # TODO: Save single_parts images to the correct folder
        # TODO: Save assemblies images either to a folder or directly to Downloads folder somehow.
        import time
        time.sleep(2)

        self.next()

    def next(self):
        # Add your logic for handling the "Finished uploading" action
        print(f"Finished uploading {self.file_types} files")

        # Call the callback function if provided
        if self.next_callback:
            self.destroy()  # Destroy the widgets of the current window
            self.next_callback()   # Show the next window

    def destroy(self):
        # Destroy all widgets in the current window
        for widget in self.root.winfo_children():
            widget.destroy()


"""For downloading the assembly images and uploading the annotations
"""
class Window2:
    def __init__(self, root, next_callback=None):
        self.root = root
        self.title = "Assembly detection"
        global assemblies

        # Download images
        welcome_label = tk.Label(root, text="1. Upload assembly images to Roboflow.")
        welcome_label.pack(pady=10)
        download_assemblies_button = tk.Button(root, text="Show assembly images to download", command=self.show_assembly_folder)
        download_assemblies_button.pack(side=tk.TOP, pady=5)

        # Manually annotate label hint
        welcome_label = tk.Label(root, text="2. Manually annotate the images with Roboflow. Export in YOLOv8 format!")
        welcome_label.pack(pady=10)
        
        # Welcome Text
        welcome_label = tk.Label(root, text="3. Select folder of extracted Roboflow export here.")
        welcome_label.pack(pady=10)
        download_assemblies_button = tk.Button(root, text="Select extracted Roboflow export folder", command=self.upload_annotated)
        download_assemblies_button.pack(side=tk.TOP, pady=5)

        # Files uploaded label
        self.images_uploaded_label = tk.Label(root, text="Images uploaded: 0")
        self.images_uploaded_label.pack(pady=[10, 0])

        self.labels_uploaded_label = tk.Label(root, text="Labels uploaded: 0")
        self.labels_uploaded_label.pack(pady=[0, 10])


        # Finished Uploading Button
        finish_button = tk.Button(root, text="Next step", command=self.next)
        finish_button.pack(side=tk.RIGHT, padx=5)

        # File Types for Upload
        self.file_types = [("Images", "*.jpg, *.png")]

        # Callback for Next Window
        self.next_callback = next_callback

    """TODO: Maybe just download the images to the downloads folder? And not the 'assembly-images' folder.
    """
    def show_assembly_folder(self):
        # Open the assembly folder, that the user should upload to Roboflow
        folder_path = FOLDER_PATH + "/assembly-images"
        show_folder(folder_path)

    def upload_annotated(self):
        folder_path = filedialog.askdirectory(title="Select Folder of Roboflow export")
        print("Selected folder path:", folder_path)

        # Then copy image and labels files to the 'combined-annotated' folder
        source_folder_path = folder_path
        destination_folder_path = os.path.join(FOLDER_PATH, "combined-annotated")
        num_images, num_labels = copy_folder(source_folder_path, destination_folder_path)

        # Update labels
        self.images_uploaded_label.config(text=f"Images uploaded: {num_images}")
        self.labels_uploaded_label.config(text=f"Labels uploaded: {num_labels}")


    def next(self):
        # Add your logic for handling the "Finished uploading" action
        print(f"Finished uploading {self.file_types} files")

        # Call the callback function if provided
        if self.next_callback:
            self.destroy()  # Destroy the widgets of the current window
            self.next_callback()   # Show the next window

    def destroy(self):
        # Destroy all widgets in the current window
        for widget in self.root.winfo_children():
            widget.destroy()




"""For preprocessing the images in the 'combined-annotated' folder. Moving them to preprocessed folder then.
"""
class Window3:
    def __init__(self, root, next_callback=None):
        self.root = root
        self.title = "Assembly detection"

        # Welcome Text
        welcome_label = tk.Label(root, text="Preprocess images. This may take a while.")
        welcome_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=20)
        self.progress_bar["maximum"] = 100
        self.progress_bar["value"] = 0

        # Create a button to start the loading
        self.start_button = tk.Button(root, text="Start preprocessing", command=self.start_preprocessing_images)
        self.start_button.pack(pady=10)


        # Finished Uploading Button
        finish_button = tk.Button(root, text="Next step", command=self.next)
        finish_button.pack(side=tk.RIGHT, padx=5)

        # Callback for Next Window
        self.next_callback = next_callback

    def start_preprocessing_images(self):
        # Hide start button
        self.start_button.pack_forget()
        
        # Create a thread for the long-running task
        import threading
        loading_thread = threading.Thread(target=self.preprocess)
        loading_thread.start()

    def preprocess(self):
        self.root.after(0, self.update_progress, 10)
        # 1. Get bounding boxes for single-parts. Put label files into 'single-parts/labels' folder.
        from get_bboxes_single_parts import create_label_files
        global CLASS_LIST
        global FOLDER_PATH

        images_path = os.path.join(FOLDER_PATH, "single-parts/images")
        labels_path = os.path.join(FOLDER_PATH, "single-parts/labels")
        CLASS_LIST = create_label_files(images_path, labels_path, CLASS_LIST)

        self.root.after(0, self.update_progress, 20)
        # 2. Add single parts folder to 'combined-annotated' folder.
        source_folder_path = os.path.join(FOLDER_PATH, "single-parts")
        destination_folder_path = os.path.join(FOLDER_PATH, "combined-annotated")
        _, _ = copy_folder(source_folder_path, destination_folder_path)

        self.root.after(0, self.update_progress, 40)
        # 3. Move + zoom of 'combined-annotated/images' images. Export to train folder.
        # TODO: Implement
        #from augment_move_and_zoom import move_and_zoom
        source_path = os.path.join(FOLDER_PATH, "combined-annotated")
        destination_path = os.path.join(FOLDER_PATH, "train")
        #CLASS_LIST = move_and_zoom(source_path, destination_path, CLASS_LIST) # TODO: Doesn't work yet...

        self.root.after(0, self.update_progress, 60)
        # 4. Add noise to 'combined-annotated/images' images. TODO: Export to train folder
        from augment_combined_images import augment_combined_folder
        combined_folder_path = os.path.join(FOLDER_PATH, "combined-annotated")
        NUM_OF_AUGMENTED_IMAGES = 2
        IMAGE_FILE_EXTENSION = ".png"
        augment_combined_folder(combined_folder_path, NUM_OF_AUGMENTED_IMAGES, IMAGE_FILE_EXTENSION)

        self.root.after(0, self.update_progress, 80)
        # 5. Preprocess 'combined-annotated/images' images. # TODO: Export to train folder
        from preprocessing import preprocess_images
        source_images_path = os.path.join(FOLDER_PATH, "combined-annotated/images")
        destination_images_path = os.path.join(FOLDER_PATH, "combined-annotated/images")
        target_resolution = (800, 450)
        preprocess_images(source_images_path, destination_images_path, target_resolution)

        self.root.after(0, self.update_progress, 100)            
        print("Done preprocessing")

    def update_progress(self, value):
        self.progress_bar["value"] = value

    def next(self):
        print("Finished preprocessing images")

        # Call the callback function if provided
        if self.next_callback:
            self.destroy()  # Destroy the widgets of the current window
            self.next_callback()   # Show the next window

    def destroy(self):
        # Destroy all widgets in the current window
        for widget in self.root.winfo_children():
            widget.destroy()


class Window4:
    """For training the YOLO model from preprocessed images in the 'train' folder.
    """
    def __init__(self, root, next_callback=None):
        self.root = root
        self.title = "Assembly detection"

        # Welcome Text
        welcome_label = tk.Label(root, text="Training the model. This might take a while, depending on training set size and number of epochs. Probably around 1 hour.")
        welcome_label.pack(pady=10)

        # Create a label to display the selected value
        self.value_label = tk.Label(root, text="Epochs to train: 0")
        self.value_label.pack(pady=10)

        # Create a slider with values from 0 to 20
        self.slider = ttk.Scale(root, from_=0, to=20, orient="horizontal", length=300, command=self.update_value)
        self.slider.pack(pady=[0,20])

        # Progress bar text
        welcome_label = tk.Label(root, text="Model training progress bar")
        welcome_label.pack(pady=10)
        # Progress bar for training
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=[0,20])
        self.progress_bar["maximum"] = 100
        self.progress_bar["value"] = 0

        # Create a button to start the loading
        self.start_button = tk.Button(root, text="Start training", command=self.start_training)
        self.start_button.pack(pady=10)

        # Open results folder
        open_results_button = tk.Button(root, text="Open results folder", command=self.show_results_folder)
        open_results_button.pack(pady=10)

        # Finished Uploading Button
        finish_button = tk.Button(root, text="Next step", command=self.next)
        finish_button.pack(side=tk.RIGHT, padx=5)

        # Callback for Next Window
        self.next_callback = next_callback

    def update_value(self, value):
        # Update the label with the selected value
        rounded_value = round(float(value))
        self.value_label.config(text=f"Selected Value: {rounded_value}")    

    def start_training(self):
        # Hide start button
        self.start_button.pack_forget()

        # Create a thread for the long-running task
        import threading
        loading_thread = threading.Thread(target=self.training)
        loading_thread.start()

    def training(self):
        global CLASS_LIST
        global FOLDER_PATH

        # Look into images folder and extract all classes
        images_folder_path = os.path.join(FOLDER_PATH, "combined-annotated/images")
        found_images = os.listdir(images_folder_path)
        found_classes = []
        for image in found_images:
            classname = image.split("_x")[0]
            if classname not in found_classes:
                found_classes.append(classname)
        CLASS_LIST = found_classes

        self.root.after(0, self.update_progress, 0)
        # 0. Create folder for everything related to the model
        # Specify the save directory for training runs
        model_path = os.path.join(FOLDER_PATH, "yolo_model")
        os.makedirs(model_path, exist_ok=True)

        # Changing directory to the folder where the model should be saved
        os.chdir(model_path)

        self.root.after(0, self.update_progress, 20)
        # 1. Set correct values in config.yaml
        config_data = {
            'train': os.path.join(FOLDER_PATH, "combined-annotated"),
            'val': os.path.join(FOLDER_PATH, "test"),
            'nc': len(CLASS_LIST),    
            'names': CLASS_LIST,
        }
        path_to_yaml = os.path.join(model_path, "config.yaml")
        with open(path_to_yaml, 'w') as file:
            yaml.dump(config_data, file)


        # TODO: Train existing model further if there exists one ? - or train new model (training new model is the default and only option for now)
        
        self.root.after(0, self.update_progress, 40)
        # 2. Train the model
        from ultralytics import YOLO
        model = YOLO("yolov8n.pt")
        slider_epochs_value = round(float(self.slider.get()))
        print("Training for num epochs:", slider_epochs_value)
        model.train(data="config.yaml", epochs=slider_epochs_value)  # train the model with specified number of epochs
        #metrics = model.val()  # evaluate model performance on the validation set


        self.root.after(0, self.update_progress, 60)
        # 3. Open the results folder
        folder_path = os.path.join(model_path, "runs/detect")
        show_folder(folder_path)

        self.root.after(0, self.update_progress, 80)
        # Going back to the original folder
        os.chdir(FOLDER_PATH)

        self.root.after(0, self.update_progress, 100)            
        print("Done training")

    def show_results_folder(self):
        # Open the results folder
        folder_path = os.path.join(FOLDER_PATH, "yolo_model/runs/detect")
        show_folder(folder_path)

    def update_progress(self, value):
        self.progress_bar["value"] = value

    def next(self):
        print("Finished training the model")

        # Call the callback function if provided
        if self.next_callback:
            self.destroy()  # Destroy the widgets of the current window
            self.next_callback()   # Show the next window

    def destroy(self):
        # Destroy all widgets in the current window
        for widget in self.root.winfo_children():
            widget.destroy()


class Window5:
    """For inference/using the trained YOLO model on some test folder.
    """
    def __init__(self, root, next_callback=None):
        self.root = root
        self.title = "Assembly detection"

        # Welcome Text
        welcome_label = tk.Label(root, text="Inference. Select a folder to make predictions for.")
        welcome_label.pack(pady=10)

        # Select which trained model to use. 
        self.model_path_label = tk.Label(root, text="Selected .pt file:")
        self.model_path_label.pack(pady=10)
        # Finished Uploading Button
        upload_button = tk.Button(root, text="Select .pt file", command=self.select_model_pt)
        upload_button.pack(side=tk.TOP, pady=5)

        self.selected_images_label = tk.Label(root, text="Selected images:")
        self.selected_images_label.pack(pady=10)
        # Select files to predict on
        upload_button = tk.Button(root, text="Select images", command=self.select_images_to_predict)
        upload_button.pack(side=tk.TOP, pady=5)

        # Create a button to start the loading
        self.start_button = tk.Button(root, text="Start predicting", command=self.predicting)
        self.start_button.pack(pady=20)

        # Open results folder
        open_results_button = tk.Button(root, text="Open results folder", command=self.show_results_folder)
        open_results_button.pack(pady=[20, 0])

        # Finished Uploading Button
        finish_button = tk.Button(root, text="Close application", command=self.next)
        finish_button.pack(side=tk.RIGHT, padx=5)

        # Callback for Next Window
        self.next_callback = next_callback

    def select_model_pt(self):
        global FOLDER_PATH

        file_type = ("Model", "*.pt")
        initial_dir = os.path.join(FOLDER_PATH, "yolo_model", "runs", "detect")
        file_paths = filedialog.askopenfilenames(title=f"Select .pt file", filetypes=[file_type], initialdir=initial_dir)
        if file_paths == type(list) and len(file_paths) > 0:
            raise Exception("Only one .pt file can be selected.")
        # Update label
        self.model_path_label.config(text="Selected .pt file: " + file_paths[0])

    def select_images_to_predict(self):
        global FOLDER_PATH

        # Select images to predict on
        file_types = [("Images", "*.jpg, *.png")]
        file_paths = filedialog.askopenfilenames(title=f"Select images to predict", filetypes=file_types, initialdir=FOLDER_PATH)
        # Display number of selected images
        self.selected_images_label.config(text=f"Selected images: {len(file_paths)}")

        # Copy images to test folder
        FOLDER_PATH = "/home/jetracer/Documents/3d_mai/application/test" # TODO: REMOVE this!
        test_folder_path = os.path.join(FOLDER_PATH, "test", "images")
        for file_path in file_paths:
            filename = file_path.split("/")[-1]
            shutil.copy(file_path, os.path.join(test_folder_path, filename))

        # Preprocess images in test/images folder
        from preprocessing import preprocess_images
        target_resolution = (800, 450)
        preprocess_images(test_folder_path, test_folder_path, target_resolution)

    def predicting(self):
        global FOLDER_PATH
        global CLASS_LIST
        os.chdir(os.path.join(FOLDER_PATH, "yolo_model"))

        # Set correct values in config.yaml
        yaml_path = os.path.join(FOLDER_PATH, "yolo_model/config.yaml")
        with open(yaml_path, 'r') as file:
            data = yaml.safe_load(file)
        data["val"] = os.path.join(FOLDER_PATH, "test")
        data["nc"] = len(CLASS_LIST)
        data["names"] = CLASS_LIST
        with open(yaml_path, 'w') as file:
            yaml.dump(data, file)

        print("Starting predicting...")
        # Predict
        from ultralytics import YOLO
        weights_path = self.model_path_label.cget("text").split(": ")[1]
        print("weights_path:", weights_path)
        yolo = YOLO(weights_path) #, imgsz=640)  # Adjust imgsz as needed
        #yolo.val(iou=0.75, conf=0.5)
        source_path = os.path.join(FOLDER_PATH, "test/images")
        #results = yolo(source_path)

        # Get all images in test/images folder
        images_to_predict = os.listdir(source_path)

        from PIL import Image
        for image in images_to_predict:        
            image_to_predict_path = os.path.join(source_path, image)
            results = yolo(image_to_predict_path)  # results list
            # Show the results
            for r in results:
                im_array = r.plot()  # plot a BGR numpy array of predictions
                im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
                im.show()  # show image
                pred_save_path = os.path.join(FOLDER_PATH, "test/predictions", image)
                im.save(pred_save_path)  # save image

        self.show_results_folder()
        os.chdir(FOLDER_PATH)
        print("Done predicting")

    def show_results_folder(self):
        # Open the results folder
        folder_path = os.path.join(FOLDER_PATH, "test", "predictions")
        show_folder(folder_path)

    def next(self):
        # Call the callback function if provided
        if self.next_callback:
            self.destroy()  # Destroy the widgets of the current window
            self.next_callback()   # Show the next window

    def destroy(self):
        # Destroy all widgets in the current window
        for widget in self.root.winfo_children():
            widget.destroy()


FOLDER_PATH = ""
CLASS_LIST = []
IMAGE_FILE_EXTENSION = ".png"

assemblies = []
single_parts = []

def main():
    root = tk.Tk()
    root.title("Assembly detection")

    # TODO: Remove
    global FOLDER_PATH
    global CLASS_LIST
    CLASS_LIST = ["asy_m4_nut_screw_10mm"] # TODO: I have to set it here manually until move_and_zoom works.

    def show_window0():
        window0 = Window0(root, show_window1)

    def show_window1():
        window1 = Window1(root, show_window2)

    def show_window2():
        window2 = Window2(root, show_window3)

    def show_window3():
        window3 = Window3(root, show_window4)

    def show_window4():
        window4 = Window4(root, show_window5)

    def show_window5():
        window5 = Window5(root, end_application)

    def end_application():
        root.destroy()
        print("Ended the application")

    # Starting with Window 0. Setting folder for storing images and model.
    show_window5()

    root.mainloop()

if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import os
import shutil # For copying files
import subprocess # For opening folder in file explorer
import platform # For checking operating system
import yaml # For editing config.yaml file

def get_class_obj(file_name):
    filename = file_name.split('/')[-1].split('.')[0]
    classname = filename.split('_x')[0]

    return classname

def clean_name(input_folder,output_folder):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        base_filename, file_extension = os.path.splitext(filename)
        name = base_filename.split("oom_")[0]+'oom'
        new_filename = name+file_extension
        old_path = os.path.join(input_folder, filename)
        new_path = os.path.join(output_folder, new_filename)
        os.rename(old_path, new_path)

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

def copy_file(source_file, destination_directory):
        try:
            # Ensure the destination directory exists
            os.makedirs(destination_directory, exist_ok=True)

            # Extract the file name from the source file path
            file_name = os.path.basename(source_file)

            # Create the destination file path
            destination_file = os.path.join(destination_directory, file_name)

            # Copy the file
            with open(source_file, 'rb') as source, open(destination_file, 'wb') as destination:
                destination.write(source.read())

            # print(f"File '{source_file}' copied to '{destination_file}' successfully.")
        except IOError as e:
            print(f"Error: {e}")

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

def find_labels_folder(folder_path):
    # Check if the given path is a directory
    if not os.path.isdir(folder_path):
        raise ValueError("Invalid folder path")

    # Function to recursively search for the 'labels' subfolder
    def search_for_labels(current_folder):
        for root, dirs, files in os.walk(current_folder):
            if 'labels' in dirs:
                return os.path.join(root, 'labels')
        
        return None

    return search_for_labels(folder_path)

def copy_label_files_from_rf(source_folder,dest_folder):

    labels_folder = find_labels_folder(source_folder)
    source_labels = os.listdir(labels_folder)
    num_labels = len(source_labels)
    dest_folder_labels = os.path.join(dest_folder,'labels_rb')
    for file in source_labels:
        source_file_path = os.path.join(labels_folder, file)
        destination_file_path = os.path.join(dest_folder_labels, file)
        try:
            shutil.copy(source_file_path, destination_file_path)
        except shutil.Error as e:
            print(f"Error copying file: {e}")
            num_labels -= 1
        except Exception as e:
            print(f"Unexpected error: {e}")
            num_labels -= 1

    yaml_files = [f for f in os.listdir(source_folder) if f.endswith('.yaml')]

    if len(yaml_files) == 1:
        #DO COPY
        yaml_files_src = [os.path.join(source_folder, file) for file in yaml_files]
        yaml_files_dest = [os.path.join(dest_folder, file) for file in yaml_files]
        shutil.copy(yaml_files_src[0], yaml_files_dest[0])
        yaml_copied = 1
    elif len(yaml_files) == 0:
        yaml_copied = 0
    else:
        yaml_copied = 2

    return num_labels,yaml_copied


"""For selecting folder where all the images and model should be stored on local machine

Creates the following folder structure:#
    - cad-files: For storing the 3D CAD files
    - assemblies: For storing the assembly images that the user has to manually annotate
    - original-images: For storing all annotated images (assemblies and single parts)
    - preprocessed: For storing all preprocessed images
    - train: TODO
"""
class Window0:
    def __init__(self, root, next_callback=None):
        self.root = root
        self.title = "Assembly detection"
        print(f'cwd: {os.getcwd()}')

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
        self.finish_button = tk.Button(root, text="Next step",state='disabled', command=self.next)
        self.finish_button.pack(side=tk.TOP, pady=5)

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
        self.finish_button.config(state="normal")

    def next(self):
        folders = [
            "cad-files","cad-files/assemblies","cad-files/single-parts",
            "assemblies","assemblies/images","assemblies/labels","assemblies/labels_rb", # Only images
            "single-parts", "single-parts/images", 
            "combined-annotated", "combined-annotated/images", "combined-annotated/labels", 
            "images_w_bounding_boxes", "images_w_bounding_boxes/single-parts", "images_w_bounding_boxes/assemblies",
            "test", "test/images", "test/predictions",
        ]
        # verify_structure = self.verify_created_structure(folders)
        # if verify_structure == False:
        self.create_folder_structure(folders)

        # Call the callback function if provided
        if self.next_callback:
            self.destroy()  # Destroy the widgets of the current window
            self.next_callback()   # Show the next window

    def verify_created_structure(self,folders):
    
        complete = True
        for folder in folders:
            folder_path = os.path.join(FOLDER_PATH,folder)
            completet = os.path.exists(folder_path)
            if completet == False:
                complete = False
                break
        return complete

    def create_folder_structure(self,folders):

        for folder in folders:
            folder_path = os.path.join(FOLDER_PATH, folder)

            # Check if the folder exists
            if os.path.exists(folder_path):
                # List files in the folder
                files = os.listdir(folder_path)
                for j in files:
                    print(f'paths {os.path.join(folder,j)} in {str(os.path.join(folder,j) in folders)}')
                fl = [item for item in files if str(os.path.join(folder,item)) not in folders]
                print(files)
                print(fl)
                if fl:
                    print(f"There are files in {folder_path}")
                    confirmation = messagebox.askyesno("Confirmation", f"Do you want to delete all files in {folder}?")
                    # Delete all files in the folder
                    if confirmation:
                        for file in fl:
                            file_path = os.path.join(folder_path, file)
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                            elif len(os.listdir(file_path)) > 0:
                                shutil.rmtree(file_path)
                            else:
                                os.rmdir(file_path)
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

        aparts,spparts = self.load_files()
        print(f'assemblies {aparts}')
        print(f'single parts {spparts}')

        # Assemblies Upload List
        assemblies_uploaded_label = tk.Label(root, text="Assemblies uploaded")
        assemblies_uploaded_label.pack(pady=[10, 0])
        self.assemblies_uploaded = tk.Listbox(root, selectmode=tk.MULTIPLE, width=40, height=10, borderwidth=2, relief="solid")
        self.assemblies_uploaded.pack(pady=0)
        upload_button = tk.Button(root, text="Upload assemblies", command=self.upload_assemblies)
        upload_button.pack(side=tk.TOP, pady=5)

        for file_path in aparts:
            file_name = file_path[0]
            print(file_name)
            self.assemblies_uploaded.insert(tk.END, file_name)
            assemblies.append(file_path)

        # Single parts Upload List
        single_parts_uploaded_label = tk.Label(root, text="Single parts uploaded")
        single_parts_uploaded_label.pack(pady=[10, 0])
        self.single_parts_uploaded = tk.Listbox(root, selectmode=tk.MULTIPLE, width=40, height=10, borderwidth=2, relief="solid")
        self.single_parts_uploaded.pack(pady=0)
        single_parts_upload_button = tk.Button(root, text="Upload single parts", command=self.upload_single_parts)
        single_parts_upload_button.pack(side=tk.TOP, pady=5)

        for file_path in spparts:
            file_name = file_path[0]
            self.single_parts_uploaded.insert(tk.END, file_name)
            single_parts.append(file_path)

        if len(spparts) > 0 and len(aparts) > 0:
            state_next = 'active'
        else:
            state_next = 'disabled'

        # Finished Uploading Button
        finish_button = tk.Button(root, text="Next step",state=state_next, command=self.create_images)
        finish_button.pack(side=tk.TOP, pady=5)


        # File Types for Upload
        self.file_types = ("3D CAD parts", "stl")

        # Callback for Next Window
        self.next_callback = next_callback

    def load_files(self):
        a_path = os.path.join(FOLDER_PATH,'cad-files','assemblies')
        sp_path = os.path.join(FOLDER_PATH,'cad-files','single-parts')
        assemlies_parts_detected = os.listdir(a_path)
        single_parts_detected = os.listdir(sp_path)
        assemlies_parts_detected = [file for file in assemlies_parts_detected if file.endswith('.stl')]
        assemlies_parts_detected = [[item, True] for item in assemlies_parts_detected]
        single_parts_detected = [file for file in single_parts_detected if file.endswith('.stl')]
        single_parts_detected = [[item, True] for item in single_parts_detected]
        return assemlies_parts_detected,single_parts_detected

    def upload_assemblies(self):
        global FOLDER_PATH
        # Open the native file dialog for uploading files
        file_paths = filedialog.askopenfilenames(title=f"Select {self.file_types} files", filetypes=[(self.file_types[0], f"*.{self.file_types[1].lower()}")])
        if file_paths:
            # Clear existing items in the list
            # self.assemblies_uploaded.delete(0, tk.END)

            # Display selected file names in the list
            for file_path in file_paths:
                file_name = file_path.split("/")[-1]
                self.assemblies_uploaded.insert(tk.END, file_name)
                asst = []
                asst.append(file_path,False)
                assemblies.append(asst)

        if(len(assemblies) > 0 and len(single_parts) > 0):
            self.finish_button.config(state = 'normal')

    def upload_single_parts(self):
        # Open the native file dialog for uploading files
        file_paths = filedialog.askopenfilenames(title=f"Select {self.file_types} files", filetypes=[(self.file_types[0], f"*.{self.file_types[1].lower()}")])
        if file_paths:
            # Clear existing items in the list
            # self.single_parts_uploaded.delete(0, tk.END)

            # Display selected file names in the list
            for file_path in file_paths:
                # Add the file path to the list
                file_name = file_path.split("/")[-1]
                self.single_parts_uploaded.insert(tk.END, file_name)
                spt = []
                spt.append(file_path,False)
                single_parts.append(spt)
        if(len(assemblies) > 0 and len(single_parts) > 0):
            self.finish_button.config(state = 'normal')


    """Creating images from 3D CAD files.
    """
    def create_images(self):
        global ASSEMBLIES_LIST
        global SINGLE_PARTS_LIST
        global assemblies
        global single_parts
        global CLASS_LIST
        global FOLDER_PATH

        # MOVING ASSEMBLIES to folder
        print(f'assemblies {assemblies}')
        print(f'single parts {single_parts}')

        for part in assemblies:
            print(part)
            if part[1] == True:
                part_name = get_class_obj(part[0])
                print(part_name)
                CLASS_LIST.append(part_name)
                ASSEMBLIES_LIST.append(part_name)
            else:
                part_name = part[0]
                print(part_name)
                class_obj = get_class_obj(part_name.split("/")[-1])
                CLASS_LIST.append(class_obj)
                ASSEMBLIES_LIST.append(class_obj)
                dest_file_ass = os.path.join(FOLDER_PATH,'cad-files','assemblies')
                copy_file(part_name,dest_file_ass)

        # MOVING SINGLE-PARTS to folder
        for part in single_parts:
            print(part)
            if part[1] == True:
                part_name = get_class_obj(part[0])
                print(part_name)
                CLASS_LIST.append(part_name)
                ASSEMBLIES_LIST.append(part_name)
            else:
                part_name = part[0]
                print(part_name)
                class_obj = get_class_obj(part_name.split("/")[-1])
                CLASS_LIST.append(class_obj)
                SINGLE_PARTS_LIST.append(class_obj)
                dest_file_ass = os.path.join(FOLDER_PATH,'cad-files','single-parts')
                copy_file(part_name,dest_file_ass)

        print(f'Class list: {CLASS_LIST}')
        # TODO: Create 2D screenshots from stl files.
        print("Creating images from 3D CAD files...")
        # Create 2D screenshots with blender
        blender_script_path = 'blender_image_creation.py'
        #blender_path = '/home/jetracer/Desktop/blender-4.0.2-linux-x64/blender'
        blender_path = 'blender'
        subprocess.run([blender_path, '--background', '--python', blender_script_path, FOLDER_PATH])

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
        self.yaml_uploaded_label = tk.Label(root, text="YAML file uploaded: ")
        self.yaml_uploaded_label.pack(pady=[10, 0])

        self.labels_uploaded_label = tk.Label(root, text="Labels uploaded: 0")
        self.labels_uploaded_label.pack(pady=[0, 10])


        # Finished Uploading Button
        finish_button = tk.Button(root, text="Next step", command=self.next)
        finish_button.pack(side=tk.RIGHT, padx=5)

        # File Types for Upload
        self.file_types = [("Images", "*.jpg *.png")]

        # Callback for Next Window
        self.next_callback = next_callback

    """TODO: Maybe just download the images to the downloads folder? And not the 'assemblies' folder.
    """
    def show_assembly_folder(self):
        # Open the assembly folder, that the user should upload to Roboflow
        folder_path = FOLDER_PATH + "/assemblies/images"
        show_folder(folder_path)

    def upload_annotated(self):
        folder_path = filedialog.askdirectory(title="Select Folder of Roboflow export")
        print("Selected folder path:", folder_path)

        # Then copy image and labels files to the 'combined-annotated' folder
        source_folder_path = folder_path
        destination_folder_labels = os.path.join(FOLDER_PATH, "assemblies")
        
        num_labels,yaml_uploaded = copy_label_files_from_rf(source_folder_path, destination_folder_labels)
        print(f'yaml - {yaml_uploaded}')

        # Update labels
        if yaml_uploaded == 1:
            test_yaml = 'Done'
        elif yaml_uploaded == 0:
            test_yaml = 'Not found'
        else:
            test_yaml = 'Not copied - Multiple YAML files founded'


        self.labels_uploaded_label.config(text=f"Labels uploaded: {num_labels}")
        self.yaml_uploaded_label.config(text=f"Labels uploaded: {test_yaml}")


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
        global ASSEMBLIES_LIST

        ## BOUNDING BOXES AND MOVING SINGLE PARTS
        bbox_path = os.path.join(FOLDER_PATH,'images_w_bounding_boxes')
        images_path = os.path.join(FOLDER_PATH, "single-parts/images")
        labels_path = os.path.join(FOLDER_PATH, "single-parts/labels")
        cl = create_label_files(images_path, labels_path, CLASS_LIST, ASSEMBLIES_LIST,bbox_path)
        print(f'cl updates single parts {cl}')

        self.root.after(0, self.update_progress, 15)
        # 2. Add single parts folder to 'combined-annotated' folder.
        # source_folder_path = os.path.join(FOLDER_PATH, "single-parts")
        # destination_folder_path = os.path.join(FOLDER_PATH, "combined-annotated")
        # _, _ = copy_folder(source_folder_path, destination_folder_path)

        ## BOUNDING BOXES ASSEMBLIES
        images_path = os.path.join(FOLDER_PATH, "assemblies/images")
        labels_path = os.path.join(FOLDER_PATH, "assemblies/labels")
        cl = create_label_files(images_path, labels_path, CLASS_LIST, ASSEMBLIES_LIST,bbox_path)
        print(f'cl updates assemblies {cl}')
        
        self.root.after(0, self.update_progress, 30)

        labels_path = os.path.join(FOLDER_PATH, "assemblies/labels_rb")
        clean_name(labels_path,labels_path)
        self.root.after(0, self.update_progress, 40)
        print('Cleaned names of labels')

        # 3. Move + zoom of 'combined-annotated/images' images. Export to train folder.
        # TODO: Implement
        from get_bboxes_single_parts import combine_move_zoom
        results_path = os.path.join(FOLDER_PATH, "combined-annotated")

        images_path = os.path.join(FOLDER_PATH, "assemblies")
        CLASS_LIST = combine_move_zoom(images_path,results_path,bbox_path,CLASS_LIST,ASSEMBLIES_LIST) # TODO: Doesn't work yet...

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
        file_types = [("Images", "*.jpg *.png *.jpeg")]
        file_paths = filedialog.askopenfilenames(title=f"Select images to predict", filetypes=file_types, initialdir=FOLDER_PATH)
        # Display number of selected images
        self.selected_images_label.config(text=f"Selected images: {len(file_paths)}")

        # Copy images to test folder
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
ASSEMBLIES_LIST = []
SINGLE_PARTS_LIST = []
single_parts = []
assemblies = []
single_parts = []

def main():
    root = tk.Tk()
    root.title("Assembly detection")

    # TODO: Remove
    global FOLDER_PATH
    global CLASS_LIST
    
    def start_application():
        show_window0()

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

    # Starting with Window 0.
    start_application()

    root.mainloop()

if __name__ == "__main__":
    main()

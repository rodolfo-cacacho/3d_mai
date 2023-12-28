import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import os
import shutil # For copying files
import subprocess # For opening folder in file explorer
import platform # For checking operating system

FOLDER_PATH = ""
CLASS_LIST = []


"""For copying a folder to another folder
Note: Make sure that the content in the destination folder is not overwritten. The content should just be appended.
Note: This is important for multiple parts of the application. That's why it's a separate function.
"""
def copy_folder(source_folder, destination_folder):
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
            "train", "train/images", "train/labels",
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
        self.file_types = [("Images", "*.jpg")]

        # Callback for Next Window
        self.next_callback = next_callback

    """TODO: Maybe just download the images to the downloads folder? And not the 'assembly-images' folder.
    """
    def show_assembly_folder(self):
        # Open the assembly folder, that the user should upload to Roboflow
        folder_path = FOLDER_PATH + "/assembly-images"
        if platform.system() == "Windows":
            subprocess.run(["explorer", folder_path], shell=True)
        elif platform.system() == "Darwin":
            subprocess.run(["open", folder_path])
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", folder_path])
        else:
            print("Unsupported operating system") 

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
        welcome_label = tk.Label(root, text="Preprocess images.")
        welcome_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=20)
        self.progress_bar["maximum"] = 100
        self.progress_bar["value"] = 0

        # Create a button to start the loading
        start_button = tk.Button(root, text="Start preprocessing", command=self.start_preprocessing_images)
        start_button.pack(pady=10)


        # Finished Uploading Button
        finish_button = tk.Button(root, text="Next step", command=self.next)
        finish_button.pack(side=tk.RIGHT, padx=5)

        # Callback for Next Window
        self.next_callback = next_callback

    def start_preprocessing_images(self):
        # Create a thread for the long-running task
        import threading
        loading_thread = threading.Thread(target=self.preprocess)
        loading_thread.start()

    def preprocess(self):
        self.root.after(0, self.update_progress, 0)
        # 1. Get bounding boxes for single-parts. Put label files into 'single-parts/labels' folder.
        from get_bboxes_single_parts import create_label_files
        global CLASS_LIST
        global FOLDER_PATH
        FOLDER_PATH = "/home/jetracer/Documents/3d_mai/application/test" # TODO: Remove
        images_path = os.path.join(FOLDER_PATH, "single-parts/images")
        labels_path = os.path.join(FOLDER_PATH, "single-parts/labels")
        CLASS_LIST = create_label_files(images_path, labels_path, CLASS_LIST)

        self.root.after(0, self.update_progress, 20)
        # 2. Add single parts folder to 'combined-annotated' folder.
        source_folder_path = os.path.join(FOLDER_PATH, "single-parts")
        destination_folder_path = os.path.join(FOLDER_PATH, "combined-annotated")
        _, _ = copy_folder(source_folder_path, destination_folder_path)

        self.root.after(0, self.update_progress, 40)
        # 3. Move + zoom of 'combined-annotated/images' images.
        


        self.root.after(0, self.update_progress, 60)
        # 4. Add noise to 'combined-annotated/images' images.
        from augment_combined_images import augment_combined_folder
        combined_folder_path = os.path.join(FOLDER_PATH, "combined-annotated")
        NUM_OF_AUGMENTED_IMAGES = 2
        augment_combined_folder(combined_folder_path, NUM_OF_AUGMENTED_IMAGES)

        self.root.after(0, self.update_progress, 80)
        # 5. Preprocess 'combined-annotated/images' images.
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

assemblies = []
single_parts = []

def main():
    root = tk.Tk()
    root.title("Assembly detection")

    def show_window0():
        window0 = Window0(root, show_window1)

    def show_window1():
        window1 = Window1(root, show_window2)

    def show_window2():
        window2 = Window2(root, show_window3)

    def show_window3():
        window3 = Window3(root, show_window1)

    # Starting with Window 0. Setting folder for storing images and model.
    show_window3()

    root.mainloop()

if __name__ == "__main__":
    main()

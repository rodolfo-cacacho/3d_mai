import tkinter as tk
from tkinter import filedialog
import shutil # For copying files

FOLDER_PATH = ""

class LoadingScreen:
    def __init__(self, root, title="Loading..."):
        self.root = root
        self.title = title

        # Create a Toplevel window for the loading screen
        self.loading_window = tk.Toplevel(root)
        self.loading_window.title("Loading")

        # Title Label
        title_label = tk.Label(self.loading_window, text=self.title)
        title_label.pack(pady=10)

        # Loading Message Label
        loading_label = tk.Label(self.loading_window, text="Loading, please wait...")
        loading_label.pack(pady=10)


"""For selecting folder where all the images and model should be stored on local machine
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
        # Call the callback function if provided
        if self.next_callback:
            self.destroy()  # Destroy the widgets of the current window
            self.next_callback()   # Show the next window

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

        # Welcome Text
        welcome_label = tk.Label(root, text="Download assembly images, manually annotate with Roboflow and then upload the annotations from Roboflow.")
        welcome_label.pack(pady=10)

        # Assemblies Upload List
        assemblies_uploaded_label = tk.Label(root, text="Assemblies uploaded")
        assemblies_uploaded_label.pack(pady=[10, 0])
        self.assemblies_uploaded = tk.Listbox(root, selectmode=tk.MULTIPLE, width=40, height=10, borderwidth=2, relief="solid")
        self.assemblies_uploaded.pack(pady=0)
        for file_path in assemblies:
            file_name = file_path.split("/")[-1]
            self.assemblies_uploaded.insert(tk.END, file_name)
        download_assemblies_button = tk.Button(root, text="Download assembly images", command=self.download_assemblies)
        download_assemblies_button.pack(side=tk.TOP, pady=5)

        # Finished Uploading Button
        finish_button = tk.Button(root, text="Next step", command=self.next)
        finish_button.pack(side=tk.LEFT, padx=5)

        # File Types for Upload
        self.file_types = [("Images", "*.jpg")]

        # Callback for Next Window
        self.next_callback = next_callback

    def download_assemblies(self):
        # Download assembly images folder to Downloads folder
        pass 
        
        

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
        window2 = Window2(root, show_window1)

    # Starting with Window 0. Setting folder for storing images and model.
    show_window0()

    root.mainloop()

if __name__ == "__main__":
    main()

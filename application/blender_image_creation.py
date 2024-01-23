import bpy
import sys
import os
import numpy as np
import math




def create_screenshots(single_parts_stl_files, assemblies_stl_files, FOLDER_PATH):
    """Create screenshots for the specified stl files. Rotate the .stl objects and save the images.
    Note: Zoom for the single parts, but don't zoom for the assemblies, since the user has to manually label the assemblies.
    """
    print("In create screenshots")
    print("single_aprts_stl_files",single_parts_stl_files)
    print("assemblies_stl_files",assemblies_stl_files)


    dir = os.path.dirname(bpy.data.filepath)
    if not dir in sys.path:
        sys.path.append(dir)

    # Set up the paths where to save the images
    single_parts_save_path = os.path.join(FOLDER_PATH,'single-parts','images')
    assemblies_save_path = os.path.join(FOLDER_PATH,'assemblies','images')

    # Set up the background
    bg_node = bpy.context.scene.world.node_tree.nodes["Background"]
    bg_node.inputs[0].default_value = (1, 1, 1, 1)  # White background
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.view_settings.view_transform = 'Standard'

    # Set up the compositor
    scene_t = bpy.context.scene
    comp_node_tree = scene_t.node_tree
    bpy.context.scene.use_nodes = True
    # Clear default nodes
    bpy.context.scene.node_tree.nodes.clear()
    node_rl_layers = bpy.context.scene.node_tree.nodes.new("CompositorNodeRLayers")
    node_alpha_over = bpy.context.scene.node_tree.nodes.new("CompositorNodeAlphaOver")
    node_alpha_over.location.x = 300
    node_alpha_over.premul = 1
    node_composite = bpy.context.scene.node_tree.nodes.new("CompositorNodeComposite")
    node_composite.location.x = 550
    bpy.context.scene.node_tree.links.new(node_rl_layers.outputs['Image'], node_alpha_over.inputs[2])
    bpy.context.scene.node_tree.links.new(node_alpha_over.outputs['Image'], node_composite.inputs['Image'])

    # Create images for single parts
    create_screenshots_for_stl_file(single_parts_stl_files, single_parts_save_path, is_assembly=False)
    # Create images for assemblies
    create_screenshots_for_stl_file(assemblies_stl_files, assemblies_save_path, is_assembly=True)

def create_screenshots_for_stl_file(stl_files, save_path, is_assembly):
    """Create images for the specified stl files and save them to the specified path.
    """
    for i_file in stl_files:
        print("Testing IO for meshes ...")
        name_part = extract_string(i_file)
        print(f'file: {i_file} part {name_part}')
        print('--- Loading model ---')
        load_model_blender(i_file,name_part)
        
        obj = bpy.data.objects[name_part]
        material_name = "met1"
        material = bpy.data.materials.get(material_name)
        
        if material is None:
            material = bpy.data.materials.new(name=material_name)
            obj.data.materials.append(material)

        # Assign the material to the object
        obj.active_material = material
        bpy.ops.object.shade_smooth(use_auto_smooth=True)
        bpy.context.object.active_material.use_nodes = True
        bpy.data.materials["met1"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.054, 0.051, 0.052, 1)
        bpy.data.materials["met1"].node_tree.nodes["Principled BSDF"].inputs[1].default_value = 0.95
        bpy.data.materials["met1"].node_tree.nodes["Principled BSDF"].inputs[2].default_value = 0.2
        bpy.data.materials["met1"].node_tree.nodes["Principled BSDF"].inputs[3].default_value = 1.45

        # Update the scene to see the changes
        bpy.context.view_layer.update()

        # Set the output directory
        bpy.context.scene.render.filepath = save_path

        # Defining the steps and range of angle values by which to rotate the point cloud.
        theta_range = np.linspace(-180, 180, 2)
        zoom_range  = np.linspace(50,95,3)
        zoom_range_names = ['z1','z2','z3']

        # Zoom and rotate
        for index,zoom in enumerate(zoom_range):
            print(index,zoom)
            # If part is an assembly - so in the assembly list - and the index is > 0 then skip it
            if (is_assembly and index > 0):
                continue

            camera_rotation = (0, 0, 0)  # Adjust as needed
            sensor_width = 128.0  # Adjust the sensor width as needed
            aspect_ratio = 16/9  # Adjust the aspect ratio as needed
            camera_location = (0, 0, zoom)  # Adjust as needed

            setup_camera(camera_location, camera_rotation, sensor_width, aspect_ratio)
            setup_lighting(camera_location,energy=zoom*0)

            steps = 5  # You can adjust this value based on your needs
            for anglex in range(steps): # X-axis
                setattr(obj.rotation_euler, 'x', math.radians(anglex * (360 / steps)))
                for angley in range(steps): #Y-axis
                    setattr(obj.rotation_euler, 'y', math.radians(angley * (360 / steps)))
                    for anglez in range(steps): # Z-axis
                        setattr(obj.rotation_euler, 'z', math.radians(anglez * (360 / steps)))
                        obj.location.x += 0  # You may need to adjust this if you want to keep the object at the same location
                        bpy.context.view_layer.update()
                        filename = f"{name_part}_x-{anglex}_y-{angley}_z-{anglez}_z-{zoom_range_names[index]}oom"
                        bpy.context.scene.render.filepath = os.path.join(save_path,filename)
                        bpy.ops.render.render(write_still=True)  

                    

### BPY Functions file

def load_model_blender(model_path,part_name):
    # Import CAD model
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    bpy.ops.import_mesh.stl(filepath=model_path)
    # Get the object by name
    obj = bpy.data.objects.get(part_name)
    # Check if the object exists
    if obj:
        # Set the object's origin to its geometry center
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

        # Optionally, set the object's location to the desired position
        obj.location = (0, 0, 0)  # Replace x, y, z with your desired coordinates
        dimensions = obj.dimensions
        print(f'{part_name} dimensions are x-{dimensions[0]} y-{dimensions[1]} z-{dimensions[2]}')

    else:
        print(f"Object '{part_name}' not found.")

def setup_camera(location, rotation, sensor_width, aspect_ratio):
    bpy.ops.object.select_by_type(type='CAMERA')
    bpy.ops.object.delete()
    bpy.ops.object.camera_add(location=location, rotation=rotation)
    bpy.context.scene.camera = bpy.context.object

    # Set camera properties
    bpy.context.scene.camera.data.sensor_width = sensor_width
    bpy.context.scene.camera.data.sensor_fit = 'HORIZONTAL'  # 'HORIZONTAL', 'VERTICAL', or 'AUTO'
    bpy.context.scene.camera.data.sensor_height = bpy.context.scene.camera.data.sensor_width / aspect_ratio

def setup_lighting(light_position, light_color=(1, 1, 1), energy=8000):
    # Add a point light at the specified position
    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete()
    bpy.ops.object.light_add(type='POINT', radius=1, align='WORLD', location=light_position)
    light = bpy.context.active_object.data
    light.energy = energy
    light.color = light_color
    light.use_nodes = False

def clean_mesh_objs():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

def set_background():
    bpy.context.scene.world.use_nodes = True
    bg_node = bpy.context.scene.world.node_tree.nodes["Background"]
    bg_node.inputs[0].default_value = (1, 1, 1, 1)  # White background


### FUNCTION READ FILES
import copy
import os
import re
import bpy

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



print("folder_path:", sys.argv[4])
folder_path = sys.argv[4]

import glob
# Get all the assemblies stl files from the folder
single_parts_path = os.path.join(folder_path,"cad-files",'single-parts')
extension = '*.stl'
search_pattern = f'{single_parts_path}/{extension}'
single_parts_stl_files = glob.glob(search_pattern)

# Get all the single parts stl files from the folder
assemblies_path = os.path.join(folder_path,"cad-files",'assemblies')
extension = '*.stl'
search_pattern = f'{assemblies_path}/{extension}'
assemblies_stl_files = glob.glob(search_pattern)

create_screenshots(single_parts_stl_files, assemblies_stl_files, folder_path)

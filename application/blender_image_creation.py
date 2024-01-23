print('------ Running script ---------')

import bpy
import sys
import os

#cwd = '/home/jetracer/Documents/3d_mai/notebooks/'
#os.chdir(cwd)
cwd = os.getcwd()
print(cwd)

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir )

import numpy as np
import math
from bpy_functions import *
from function_read_files import *


cwd = os.getcwd()
parent_dir = os.path.dirname(cwd)
data_path = parent_dir+'/data/'
cad_path = data_path + 'cad-models-threads/'
file_extension = '.stl'
path_save = data_path+'test_threads/imagesO/'
files = get_files_in_subdirectories(cad_path,file_extension)

exists = create_folder_if_not_exists(path_save)
if exists:
    images_del = get_files_in_subdirectories(path_save,'png')
    for imdel in images_del:
        delete_file(imdel)

# Defining the steps and range of angle values by which to rotate the point cloud.
theta_range = np.linspace(-180, 180, 2)
zoom_range  = np.linspace(50,95,3)
zoom_range_names = ['z1','z2','z3']
# Set up the background
#bpy.context.scene.world.use_nodes = True
#bpy.context.space_data.shading.use_scene_lights = True
#bpy.context.space_data.shading.use_scene_world = False
bg_node = bpy.context.scene.world.node_tree.nodes["Background"]
bg_node.inputs[0].default_value = (1, 1, 1, 1)  # White background
bpy.context.scene.render.film_transparent = True
bpy.context.scene.view_settings.view_transform = 'Standard'

scene_t = bpy.context.scene
comp_node_tree = scene_t.node_tree
bpy.context.scene.use_nodes = True

bpy.context.scene.node_tree.nodes.clear()

node_rl_layers = bpy.context.scene.node_tree.nodes.new("CompositorNodeRLayers")

node_alpha_over = bpy.context.scene.node_tree.nodes.new("CompositorNodeAlphaOver")
node_alpha_over.location.x = 300
node_alpha_over.premul = 1

node_composite = bpy.context.scene.node_tree.nodes.new("CompositorNodeComposite")
node_composite.location.x = 550

bpy.context.scene.node_tree.links.new(node_rl_layers.outputs['Image'], node_alpha_over.inputs[2])
bpy.context.scene.node_tree.links.new(node_alpha_over.outputs['Image'], node_composite.inputs['Image'])


for i_file in files:
    
    # Set up the camera
    
    camera_rotation = (0, 0, 0)  # Adjust as needed
    sensor_width = 128.0  # Adjust the sensor width as needed
    aspect_ratio = 16/9  # Adjust the aspect ratio as needed
    
    
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
#    bpy.context.object.active_material.name = "met1"

    bpy.ops.object.shade_smooth(use_auto_smooth=True)
    bpy.context.object.active_material.use_nodes = True
    bpy.data.materials["met1"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.054, 0.051, 0.052, 1)
    bpy.data.materials["met1"].node_tree.nodes["Principled BSDF"].inputs[1].default_value = 0.95
    bpy.data.materials["met1"].node_tree.nodes["Principled BSDF"].inputs[2].default_value = 0.2
    bpy.data.materials["met1"].node_tree.nodes["Principled BSDF"].inputs[3].default_value = 1.45
    
#    obj.active_material = material


    # Update the scene to see the changes
    bpy.context.view_layer.update()
    

    # Set the output directory
    bpy.context.scene.render.filepath = path_save

    # Set the number of steps for each axis
    steps = 5  # You can adjust this value based on your needs
    
    for index,zoom in enumerate(zoom_range):
        print(index,zoom)
        
        camera_location = (0, 0, zoom)  # Adjust as needed
        setup_camera(camera_location, camera_rotation, sensor_width, aspect_ratio)
        setup_lighting(camera_location,energy=zoom*0)
        if(index > 0 and 'asy' in name_part):
            continue
        for anglex in range(steps): # X-axis
            setattr(obj.rotation_euler, 'x', math.radians(anglex * (360 / steps)))
            for angley in range(steps): #Y-axis
                setattr(obj.rotation_euler, 'y', math.radians(angley * (360 / steps)))
                for anglez in range(steps): # Z-axis
                    setattr(obj.rotation_euler, 'z', math.radians(anglez * (360 / steps)))
                    obj.location.x += 0  # You may need to adjust this if you want to keep the object at the same location
                    bpy.context.view_layer.update()
                    filename = f"{name_part}_x-{anglex}_y-{angley}_z-{anglez}_z-{zoom_range_names[index]}oom"
                    bpy.context.scene.render.filepath = path_save + filename
                    bpy.ops.render.render(write_still=True)  
                    
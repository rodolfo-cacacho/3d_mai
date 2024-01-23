import bpy

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


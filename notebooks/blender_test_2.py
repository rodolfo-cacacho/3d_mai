import bpy
import math


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

# Example usage
model_path = '/Users/rodolfocacacho/Documents/Documents/MAI/Project module/3d_mai/data/cad-models-threads/assembly_m4_nut_screw_10mm/m4_nut_screw_10mm.stl'
output_path = '/Users/rodolfocacacho/Documents/Documents/MAI/Project module/3d_mai/data/test_images_blender'
num_rotations = 8
num_zooms = 4

bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Set up the background
bpy.context.scene.world.use_nodes = True
bg_node = bpy.context.scene.world.node_tree.nodes["Background"]
bg_node.inputs[0].default_value = (1, 1, 1, 1)  # White background

# Import CAD model
bpy.ops.import_mesh.stl(filepath=model_path)

# Replace 'your_imported_object' with the name of the imported object
object_name = 'm4_nut_screw_10mm'

# Get the object by name
obj = bpy.data.objects.get(object_name)

# Check if the object exists
if obj:
    # Set the object's origin to its geometry center
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

    # Optionally, set the object's location to the desired position
    obj.location = (0, 0, 0)  # Replace x, y, z with your desired coordinates
    dimensions = obj.dimensions
    print(f'{object_name} dimensions are x-{dimensions[0]} y-{dimensions[1]} z-{dimensions[2]}')

else:
    print(f"Object '{object_name}' not found.")


# Set up the camera
camera_location = (0, 0, 15)  # Adjust as needed
camera_rotation = (0, 0, 0)  # Adjust as needed
sensor_width = 128.0  # Adjust the sensor width as needed
aspect_ratio = 16/9  # Adjust the aspect ratio as needed
setup_camera(camera_location, camera_rotation, sensor_width, aspect_ratio)
setup_lighting(camera_location)

path_test_image = '/Users/rodolfocacacho/Documents/Documents/MAI/Project module/3d_mai/data/test_images_blender/img_test.png'
#bpy.context.scene.render.filepath = path_test_image
#bpy.ops.render.render(write_still=True)



# Function to render images from different angles and zooms
def render_images(output_path, num_rotations, num_zooms):
    for zoom in range(1, num_zooms + 1):
        zoom_factor = zoom / 2.0

        for rotation in range(num_rotations):
            angle = rotation * 2 * math.pi / num_rotations

            # Rotate model
            obj.transform.rotate(value=angle, orient_axis='X')
            obj.transform.rotate(value=angle, orient_axis='Y')
            obj.transform.rotate(value=angle, orient_axis='Z')

            # Set camera zoom
            bpy.context.scene.camera.location = (
                zoom_factor * 5 * math.cos(angle),
                zoom_factor * -5 * math.sin(angle),
                zoom_factor * 5
            )

            # Set output file path
            bpy.context.scene.render.filepath = f"{output_path}/render_zoom{zoom}_rot{rotation}.png"

            # Render the image
            bpy.ops.render.render(write_still=True)

            # Reset rotations
            bpy.ops.object.rotation_clear()



## Set up the scene
#setup_scene(model_path)

## Render images
render_images(output_path, num_rotations, num_zooms)


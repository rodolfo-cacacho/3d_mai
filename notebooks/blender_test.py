import bpy
import math

# Function to set up the scene
def setup_scene(model_path):
    # Clear existing mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    # Import CAD model
    bpy.ops.import_mesh.stl(filepath=model_path)

    # Set up camera
    bpy.ops.object.camera_add(location=(5, -5, 5), rotation=(math.radians(60), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.object

# Function to render images from different angles and zooms
def render_images(output_path, num_rotations, num_zooms):
    for zoom in range(1, num_zooms + 1):
        zoom_factor = zoom / 2.0

        for rotation in range(num_rotations):
            angle = rotation * 2 * math.pi / num_rotations

            # Rotate model
            bpy.ops.transform.rotate(value=angle, orient_axis='X')
            bpy.ops.transform.rotate(value=angle, orient_axis='Y')
            bpy.ops.transform.rotate(value=angle, orient_axis='Z')

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

# Example usage
model_path = '/Users/rodolfocacacho/Documents/Documents/MAI/Project module/3d_mai/data/cad-models-threads/assembly_m4_nut_screw_10mm/m4_nut_screw_10mm.stl'
output_path = '/Users/rodolfocacacho/Documents/Documents/MAI/Project module/3d_mai/data/test_images_blender'
num_rotations = 8
num_zooms = 4

# Set up the scene
setup_scene(model_path)

# Render images
render_images(output_path, num_rotations, num_zooms)


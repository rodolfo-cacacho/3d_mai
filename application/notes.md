# Notes on application

Note:
- Building it with tkinter python package because of its easy usage and big community.

Goal:
- Having a GUI that the user can interact with. 
- The GUI should then call the appropriate python functions.
- THe GUI should guide the user through the workflow from start (3D CAD files) to finish (detection with camera).

Workflow:
1. Uploading 3D CAD files. Automatically rotate and create screenshots from that.
2. Manually label a few assemblies.
3. Preprocessing:
    - Augmentation: Move + zoom. Also add noise as preprocessing step.
    - Preprocess the images. 16:9 images with at least 800x450. Contour detection.
4. Train the model with these.
5. Detection: Also preprocess the testing images and predict with YOLO.

TODO:
- Maybe I should store the manually annotated images somewhere, so they don't get lost. Right now I'm only storing the single-parts images and labels separately.


TODO's open and important:
    - Selecting testing folder, which then copies the images to a testing folder. Then the images have to be preprocessed - very important
    - Creating 2D screenshots from 3D CAD
    - And moving and zooming augmentation aren't done yet

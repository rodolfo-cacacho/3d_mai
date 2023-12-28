# Notes on application

Note:
- Building it with tkinter python package because of its easy usage and big community.

Goal:
- Having a GUI that the user can interact with. 
- The GUI should then call the appropriate python functions.
- THe GUI should guide the user through the workflow from start (3D CAD files) to finish (detection with camera).

Workflow:
1. Uploading 3D CAD files. (Somehow checkbox for assemblies?). Automatically rotate and create screenshots from that. Note: Probably need blender for that somehow. TODO: Ask Rodolfo.
2. Manually label a few assemblies.
3. Preprocessing:
    - Augmentation: Move + zoom. Also add noise as preprocessing step.
    - Preprocess the images. 16:9 images with at least 800x450. Contour detection.
4. Train the model with these.
5. Detection: Also preprocess the teting images and predict with YOLO.

Next TO DO's:
- Convert the .ipynb files to .py files containing the important python functions.
- Build basic GUI that the user can interact with. GUI should call the python functions.
- All of the images should be stored to folders on the device - kind of like how it's done right now.

Basic GUI functions/views:
- database should be easy folder structure
- views:
    - Upload 3D CAD files; Somehow label assemblies; Return/Download assembly images so user can upload it to roboflow
        - Maybe two separate buttons. One for normal objects and one for assemblies.
        - This has to automatically take the 2D screenshots from the different angles.
        - Then the user should be able to download the assembly images. And upload them to roboflow.
        - Some python folder magic has to be done here.
    - User should then upload the annotated assemblies somehow
        - Some python folder magic has to be done here.
    - Then training view. Which somehow should display a progress/ estimated time to finish/ ...
        - Do the preprocessing + show progress on how it's going
        - This should run some test/ show which images/ how many images there are
    - Then testing view. User should then upload testing images; GUI should display predictions somehow or export it somehow.
    - User should also be able to upload an additional 3D CAD model - maybe user just has to retrain everything.

State 27.12 to continue tommorow from:
- window0: Select folder where everything should be stored to
- window0: Setup correct folder structure and start with manually adding raw screenshots to there (some that I already have)
- window1: Select assemblies and single parts 3D CAD files; TODO: Create 2D screenshots from that and save to correct folders. TODO: assemblies to assemblies folder and single parts to orginal images folder
- window2: Download the assmbly images somehow to the Downloads folder. So that user can upload them easily to Roboflow for manual labeling.
- TODO: Then: Upload images and labels folders from Roboflow.
- TODO: Preprocessing (adding noise); ...
- TODO: Create perfect training setup
- TODO: Train model

# Summary of the project
Here we want to summarize the work, to have all of the information needed for writing the paper in one place.

## Architecture
![Screenshot from 2024-01-13 12-20-50](https://github.com/rodolfo-cacacho/3d_mai/assets/67323507/9c568df2-0d13-467f-9b7f-220e34af60a7)

The user can input 3D CAD files of objects. These objects can either be individual parts (like a screw, nut, ...) or an assembly (screw + nut). 

For the individual parts the pipeline is fully automated with no human intervention needed. 2D screenshots of the objects are created with the goal of seeing the objects from multiple angles, in different sizes and in different places in the 2D screenshot. The goal is to get as close to pictures of the real objects as possible. These 2D screenshots with its annotations will then be used as training data. 

The pipeline for the individual parts are as follows: 
1. 3D: Rotate part and take 2D screenshots (To see the objects from different angles). These 2D screenshots will be used for the rest of the pipeline.
2. Automatically detecting the bounding box around the object in the 2D image. For this the open-source package open-cv is used.
3. Now, after extracting the bounding box, we move the object to other places within the image, and zoom in and zoom out. Note that while augmenting the object within the image, we can always calculate where the bounding box should end up, so we always have the perfect bounding box around the object. State: Seeing object from different angles and in different sizes, while always having the perfect bounding box around the object.
4. Adding noise to the screenshots. This is an important step for addressing the Simulation to Reality problem. The idea of adding noise to the simulation to make it closer to reality is called "Domain adaptation" in the "Sim2Real" research branch. This is done to account for randomness in the real images, like lighting, shadows, and so on.
5. Now we extract the contours of the object with the open-source package open-cv. The result is a binary image where the contours of the object are 1 (white), while everything else is 0 (black). Note: Adding noise before this step was important, since the contour detection is not able to detect the edges perfectly anymore, which resembles what happens when extracting the contours of images of real images. Without the two steps of adding noise and extracting contours after, the simulation images don't look close enough to the real images, which results in a poor performing model, when it is only trained on simulation data and then tries to predict real objects.
6. State: We have training data of the object from different angles, different sizes, extracted (not-perfect) contour which resembles real images, and we have the perfect bounding boxes around each object. This is then the data the model is trained with.

The pipeline for assemblies: 
The pipeline for assemblies is almost the same as for the individual parts. The only difference is that the bounding boxes cannot be automatically extracted by open-cv. Therefore the user has to manually label (i.e. draw bounding boxes) around the individual parts of the assembly images. This manual labeling should be done in the free software roboflow (roboflow.com) which specializes in manually annotating images. The annotated images can then be exported using the YOLOv8 format from the roboflow website, containing the label files with the annotated bounding boxes. This exported folder is then added to the training data of the individual parts to train the model.

Inference/ prediction of real images: 
The goal of the project is to predict real objects in real images. To be able to predict the bounding boxes and classes of the objects in the real images, the real images have to be preprocessed, in order to look similar to the training images. The only preprocessing step needed in the contour-detection using the open-source package open-cv. The preprocessed images can then be used for prediction by the model.


## Big problems we had to solve
### Simulation to reality (Sim2Real) 
We want to create the training images from 3D CAD files of the objects. Problem: The objects are perfect and don't have any defects, which is not the same when taking real images (which we want to classify at the end).

There is a big research branch calles "Simulation to reality" (Sim2Real) that concerns the problem of closing the gap between the simulation data and data from the real world.
We used the adding noise idea of "domain adaptation" in Sim2Real research. This is the simple idea of adding noise to the simulation data, which hopefully makes the simulation data more like the real data.

### From 3D objects to training images. Almost fully automated.
We want to automate as much as possible so the user has to do as little as possible. With the solution we came up with the user only has to label 125 images of assemblies manually (which takes around 30 minutes). Everything we were able to automate.


## Outlook: Possible improvements
### Fine-tuning model that was pretrained on similar task 
We trained a model from scratch. We could have used a model that was pretrained on similar task of detecting manufacturing parts and fine-tuned that model. 
This would arguably result in a better model because of the latest finding about foundational models and fine-tuning (TODO: Add source here for sure).

### Other approaches of Sim2Real to make the simulation images closer to real images
Talk a little bit about other branches of the Sim2Real reseach. For example to use GANs to add the style of the real images to the simulation images. 
(TODO: Read more about Sim2Real, talk about some approaches add sources of course.)
(Note: We had good slides about this in Embedded Systems class, I will send them to you.)

### More training images with bigger model; Adjusting Hyperparameters
We only used 4 different parts, for which we used around 3.000 training images to train the model.
Furthermore we only used quite a small model. So it only took around one hour to train on CPU (with 2017 Macbook Pro).
Of course we could use more training images, a bigger model and train it for longer. This would arguably result in a better model, but we haven't tried it out (TODO: Add some source here that underlines it).


## Results 
See 
### Confusion matrix 
![confusion_matrix](https://github.com/rodolfo-cacacho/3d_mai/assets/67323507/88ec2bbf-e089-4b60-9bd3-be447fa61a1c)

### Training and validation Loss
![results](https://github.com/rodolfo-cacacho/3d_mai/assets/67323507/14c91f1b-af4f-4663-b1eb-c215ad01f65d)

### Precision-Recall curve
![PR_curve](https://github.com/rodolfo-cacacho/3d_mai/assets/67323507/dadcc5ea-edb7-42e3-b320-60576cf319f7)

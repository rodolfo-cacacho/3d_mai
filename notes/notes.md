# Notes/ Running Powerpoint
In this file we collect our decisions and notes while working on the project, so we have everything in a centralized place and don't have to recall or search for stuff when it comes to writing the paper

### 23-10-08 Bounding boxes for the 2d Images and using YOLO model

We read more about object detection and we learned that there are the two popular architectures:
- YOLO (You only look once) 
- R-CNN (One model for attention proposal + one model for object detection)
  
Since YOLO is said to be simpler to implement and reach a near instant prediction time, we decided on first trying out the YOLO model.
Although the YOLO model is probably less accurate than the R-CNN model. If we have time later in the project, we want to try out R-CNN, too.

References:
- YOLO paper: https://arxiv.org/abs/1506.02640
- YOLO version 1 to 8: https://www.mdpi.com/2075-1702/11/7/677  

**Outcome**:
- We created training images with bounding boxes and collected it in the folder and file structure that is expected by YOLOv8
- Then we trained a YOLOv8 Nano model for 3 epochs with around 2000 images of four different objects.
- These are the predictions for some of the images:

Predicted bounding boxes and objects             |  Confusion matrix
:-------------------------:|:-------------------------:
![val_batch1_pred](https://github.com/rodolfo-cacacho/3d_mai/assets/67323507/0ba5ad68-611f-4b49-8f4d-8a51523a3c3c) | ![confusion_matrix](https://github.com/rodolfo-cacacho/3d_mai/assets/67323507/3e186b16-b319-4822-945f-7404c3274647)

- The results are quite good, even for two screws that only differ in their size. But the predictions are obviously not perfect yet.

Limitations still:
- The objects are a constant size and they are only in the middle of the image. Images are not augmented at all, which will result in bad predictions for real images.
- The training images are very far from what real images in the manufacturing environment will look like.
- The model trains for quite long (> 20 mins) on my Macbook Pro 2017. Since the training pipeline is not optimized and also since GPU isn't used.
- The validation images are very close to the training images (maybe they are even the same in many cases), since there are 2.000 images of each object and they are only rotated. Logically the objects are exactly the same when the object is turned by 360 degrees.

---
### 23-11-02 Further preprocessing and Flowcharts

We want to extend the preprocessing phase to come close to real world images, by:
- Moving object around in 2D image
- Change lighting and material of 3D object
- Change background of 2D image to real world background

Also we want to document the preprocessing and model architecture by flowcharts.

**Outcome**:

Preprocessing pipeline             |  Object detection/ Classification pipeline
:-------------------------:|:-------------------------:
![Flowchart-preprocessing drawio](https://github.com/rodolfo-cacacho/3d_mai/assets/67323507/44be0e74-c991-483e-acd4-73a4a0cc575b)  |  ![Flowchart-classification drawio](https://github.com/rodolfo-cacacho/3d_mai/assets/67323507/e298eee8-7e14-4609-b6e2-8367fbd271b8)




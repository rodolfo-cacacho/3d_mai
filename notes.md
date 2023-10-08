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


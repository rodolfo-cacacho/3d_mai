# Summary of the project
Here we want to summarize the work, to have all of the information needed for writing the paper in one place.

## Flowchart of the final architecture


## Results 


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

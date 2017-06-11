[//]: # (Image References)

[image1]: ./misc/rover_image.jpg
[image2]: ./misc/segmented_images.jpg
[image3]: ./misc/rover_sim_config.jpg
[image4]: ./misc/example_run.jpg



## Project1: Search and Sample Return

---
![rover][image1]

**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  


## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation. 

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

I converted the image to HSV color to help with the rock_sample segementation. I used skimage.measure.regionprops to choose the largest area feature (and fill-in holes) to help with the segmentation. For example if multiple rocks appear in the image frame, only one would be detected. 


Examples of image segmentation (white area are the features of interest):

![segmented images][image2]

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 

The white pixels from the segemented BW images of the navigable terrain, obstacles, and rocks were mapped from the rover's camera image reference frame to the overhead world-view refence-frame using the appropriate scale, and rotation/translation matrices. The world map was created by equating each rgb channel with the segmemented BW image of the obstacles, obstacles, and rock

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

Key points of `perception_step()`:
-To ensure fidelity, the worldmap would only get updated if the rover's roll and pitch were within certain limits
-To prevent the rover from seeing side-paths too far in advance, the navigable-terrain was clipped

Key points of `decision_step()`:
- Implemented wall-hugging. This ensured the entire area would be transversed. It also simplified some of the decision making.
- Right-side wall-hugging was accomplished by using the 39% quantile of the navigable_terrain angles cipped at -15 and +12 degrees. The value of the quantiles was choosen so it would favor the right-side and right-turns but not be too close to the wall. It often provided a reasonable angle-of-attack when navigating to rock_samples.
- Rover speed was set low at 0.7m/s to help with rock_sample finding. The acceleration was set high at 0.4 m/s/s to help the rover from getting stuck
- Obstacle avoidance was accomplished by setting a minimum for the navigable area.  
- When a rock was detected, the rover would use the angle in the camera to move towards it at low velocity (stop and start)
- After a rock was picked-up, the rover was instructed to go backwards to help it regain a suitable position
- Some routines for getting the rover un-stuck were implemented. These involved temporarily increasing the acceleration, going backward, and rotating the rover. They were developed by trial-error. It could also get stuck turning large circles in open-field regions. An attempt has been made to break this looping.



#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

FPS = 12
![simulator settings][image3]


Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  

The approach was to:
- Follow the wall to ensure the rover would complete the course efficiently (use quantile of navigable angles when steering)
- Use image semgmentation to find the rock_samples, navigable_terrain
- If a rock is detected, try to pick it up even if it is on opposite wall (left-side)
- Have low velocity with large acceleration (seemed to work best)
- Not use images when the rover is pitching or rolling to much when constructing the worldmap 

Further improvements:
- Need to identify hazards better. Maybe use pattern recognition(template matching, edge shape etc). Maybe quantify left,right, and center area/horizon
- Even though there has been an attempt to prevent the rover from re-tracing its path, it is far from perfect. I would be better to store the rover positions
- Not all of the stuck-rover possibilities have been tested. So it still may get stuck. It is probably better to be more cautious and spend more effort on developing  hazard detection.
- Double-check the robustness of the segmentation on many images
- Need to explore deep learning methods 



![Example Run][image4]



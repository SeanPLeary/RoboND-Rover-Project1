import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_terrain = np.array([130,130,130])
    upper_terrain = np.array([255,255,255])


    threshed_terrain = cv2.inRange(img, lower_terrain, upper_terrain)
   
    #kernel = np.ones((5,5),np.uint8)
    #threshed_terrain = cv2.morphologyEx(threshed_terrain, cv2.MORPH_CLOSE, kernel)
    
    import skimage
 
    from skimage.filters import median
    from skimage.measure import regionprops 
    from skimage.measure import label
    from skimage.morphology import rectangle
    
    threshed_terrain = skimage.filters.median(threshed_terrain,rectangle(3,7))
    
    bw_label = skimage.measure.label(threshed_terrain)
    stats = skimage.measure.regionprops(bw_label,intensity_image = threshed_terrain)
    
    
    # take maximum area only
    max_area = 0
    
    for stat in stats:
        if stat.area > max_area:
            max_area = stat.area
            max_bbox = stat.bbox
            filled_image = stat.filled_image
            extent = stat.extent
            orientation = stat.orientation
            euler_number = stat.euler_number
            intensity_image = stat.intensity_image
  
    try:
        (start_x, start_y, end_x, end_y) = max_bbox
        mask1 = np.zeros_like(threshed_terrain)
        mask2 = np.zeros_like(threshed_terrain)
        mask1[start_x:end_x,start_y:end_y] = intensity_image
        mask2[start_x:end_x,start_y:end_y] = filled_image
  
        threshed_terrain = mask2
  
    except:
        pass

    
    lower_rock = np.array([90,200,100])
    upper_rock = np.array([100, 255, 230])
    threshed_rock = cv2.inRange(hsv, lower_rock, upper_rock)
    kernel = np.ones((6,6),np.uint8)
    threshed_rock = cv2.dilate(threshed_rock,kernel,iterations = 1)

    bw_label = skimage.measure.label(threshed_rock)
    stats = skimage.measure.regionprops(bw_label,intensity_image = threshed_rock)
    
    # take maximum area only (incase there are more than one rock in an image)
    max_area = 0
    
    for stat in stats:
        if stat.area > max_area:
            max_area = stat.area
            max_bbox2 = stat.bbox
            filled_image2 = stat.filled_image
            intensity_image2 = stat.intensity_image
    try:
        (start_x, start_y, end_x, end_y) = max_bbox2
        mask1 = np.zeros_like(threshed_rock)
        mask2 = np.zeros_like(threshed_rock)
        mask1[start_x:end_x,start_y:end_y] = intensity_image2
        mask2[start_x:end_x,start_y:end_y] = filled_image2
        threshed_rock = mask2
    except:
        pass

    print(max_area)
    lower_sky = np.array([80,1,90])
    upper_sky = np.array([200, 40, 140])
    threshed_sky = cv2.inRange(hsv, lower_sky, upper_sky)
    threshed_sky = cv2.morphologyEx(threshed_sky, cv2.MORPH_OPEN, kernel)
 
   
    threshed_obstacle = np.logical_not(np.logical_or(np.logical_or(threshed_terrain,threshed_sky),threshed_rock))
  

    #bw_obstacle = cv2.morphologyEx(bw_obstacle, cv2.MORPH_OPEN, kernel)
    
    return (threshed_terrain*255, threshed_obstacle*255, threshed_rock*255)



# Define a function to convert to rover-centric coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to apply a rotation to pixel positions
def rotate_pix(xpix, ypix, yaw):
    # TODO:
    # Convert yaw to radians
    yaw_rad = np.radians(yaw)
    # Apply a rotation
    #xpix_rotated = 0
    #ypix_rotated = 0
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))                     
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
	
    return xpix_rotated, ypix_rotated

# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # TODO:
    # Apply a scaling and a translation
    #xpix_translated = 0
    #ypix_translated = 0
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated

# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    (xpix_rot, ypix_rot) = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped

from skimage import feature
from skimage import measure
from skimage.transform import hough_line, hough_line_peaks
# nav_terrain edge
def bw_perim(bw):
    conts = measure.find_contours(bw, 0.5)
    contour_image = np.zeros_like(bw)

    for c in conts:
        c = np.round(c).astype(int)
        coords = (c[:, 0], c[:, 1])
        contour_image[coords] = 1
        
    (h,theta,d) = hough_line(contour_image)
    try:
        (_,angle,dist) = hough_line_peaks(h,theta,d,num_peaks=1)
    except:
        (_,angle,dist) = (float('Inf'),float('Inf'),float('Inf'))
    return (angle,dist,contour_image)
    


#######


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
	
    # 1) Define source and destination points for perspective transform
    dst_size = 5
    bottom_offset = 6
    source_pts = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination_pts = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset], 
                      [Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                      ])
	
    # 2) Apply perspective transform
    rover_worldview  = perspect_transform(Rover.img, source_pts, destination_pts)
	
	
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    (threshed_terrain,threshed_obstacles,threshed_rocks) = color_thresh(rover_worldview)	
	
 
#    (numrow,numcol) = threshed_terrain.shape
#    #threshed_terrain[:,1:int(numcol/2)] = 0
#    threshed_terrain[1:int(numrow/4),:] = 0
#    (terrain_x_cam, terrain_y_cam) = rover_coords(threshed_terrain)
  
	
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
    #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
    #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
    Rover.vision_image[:,:,0] = threshed_obstacles
    Rover.vision_image[:,:,1] = threshed_rocks
    Rover.vision_image[:,:,2] = threshed_terrain
		
    # 5) Convert map image pixel values to rover-centric coords
    (terrain_x_cam, terrain_y_cam) = rover_coords(threshed_terrain)
    (obstacles_x_cam, obstacles_y_cam) = rover_coords(threshed_obstacles)
    (rocks_x_cam, rocks_y_cam) = rover_coords(threshed_rocks)	
	
    # 6) Convert rover-centric pixel values to world coordinates
    scale = dst_size*2
   
    (terrain_x_world, terrain_y_world) = pix_to_world(terrain_x_cam, terrain_y_cam, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], scale)
    (obstacles_x_world, obstacles_y_world) = pix_to_world(obstacles_x_cam, obstacles_y_cam, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], scale)
    (rocks_x_world, rocks_y_world) = pix_to_world(rocks_x_cam, rocks_y_cam, Rover.pos[0], Rover.pos[1], Rover.yaw,Rover.worldmap.shape[0], scale)

    
   
	
    # 7) Update Rover worldmap (to be displayed on right side of screen)
    # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
    #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
    #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    
    if (abs(Rover.roll) <= 0.08 or abs(Rover.roll) >= 360-0.08) and (abs(Rover.pitch) <= 0.08 or abs(Rover.pitch) >= 360-0.08):     
        Rover.worldmap[obstacles_y_world, obstacles_x_world, 0] = 255   
        Rover.worldmap[rocks_y_world, rocks_x_world, 1] = 255    
        Rover.worldmap[terrain_y_world, terrain_x_world, 2] = 255
        
   
    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
    # Rover.nav_dists = rover_centric_pixel_distances
    # Rover.nav_angles = rover_centric_angles
        
      
        
    (Rover.nav_dists, Rover.nav_angles) = to_polar_coords(terrain_x_cam, terrain_y_cam)
    (Rover.rock_dists, Rover.rock_angles) = to_polar_coords(rocks_x_cam, rocks_y_cam)
    (Rover.obstacles_dists, Rover.obstacles_angles) = to_polar_coords(obstacles_x_cam, obstacles_y_cam)
    
    
    
   # Clipped angles when distance is larger than 30
    try:
        inds = Rover.nav_dists < np.percentile(Rover.nav_dists,30)
        Rover.nav_angles = Rover.nav_angles[inds]
    except:
        pass
    
    #nav terrain boundary
    (threshed_terrain,threshed_obstacle,threshed_rock) = color_thresh(Rover.img)
    (angle,dist,contour_image) = bw_perim(threshed_terrain)
    (numrows,numcols) = contour_image.shape
    (ypos, xpos) = contour_image.nonzero()
    
  
  
        
        
      
    return Rover
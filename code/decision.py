import numpy as np
import time
from random import random


# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function


    

def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
  
    
    if Rover.home_pos is None:
        # get home starting position
        Rover.home_pos = Rover.pos
        Rover.prev_pos = Rover.pos
        
    # Put brakes on if velocity is too high (usually after escaping hazard w/ high throttle)
    if abs(Rover.vel) > Rover.max_vel:
        Rover.throttle = 0
    if abs(Rover.vel) > Rover.max_vel*1.5:
        Rover.brake = Rover.brake_set
    if abs(Rover.vel) > Rover.max_vel*2:
        Rover.brake = Rover.brake_set*2
  

  
 
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True

        
    # Check if rock sample has been detected
    if Rover.rock_angles is not None:
        if Rover.mode == 'pick-up' and len(Rover.rock_angles) < 1 and not Rover.picking_up:
            Rover.brake = 0
            Rover.throttle = Rover.throttle_set/2
            Rover.loop_counter = 0
            Rover.mode = 'stop'


        if len(Rover.rock_angles) > 1 and not Rover.picking_up:
            print("Sample pick-up")
            Rover.mode = 'pick-up'
            # Steer towards sample using mean of angles to rock
            Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)
           
            Rover.brake = 0
            
            # If within range of arm or velocity is too high, brake to stop/slow-down
            if Rover.near_sample:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set*2  
            elif Rover.vel > Rover.max_vel/2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set/2
            else: # accelerate
                Rover.brake = 0
                Rover.throttle = Rover.throttle_set/2
            
            #If Rover is stuck
            if Rover.vel < 0.1 and Rover.throttle > 0:
                Rover.loop_counter += 1
                if Rover.loop_counter > 30:
                    print('stuck')
                    Rover.steer = random()*30-15
                    Rover.brake = 0
                    Rover.throttle = Rover.throttle_set*2
                    time.sleep(0.5)
                    if Rover.vel > Rover.max_vel/2:  
                        Rover.throttle = 0
                        Rover.brake = Rover.brake_set*2
                        time.sleep(2)
                        Rover.brake = 0
                        Rover.throttle = 0
                        Rover.loop_counter = 0
                        Rover.mode = 'stop'
                                                                        
                if Rover.loop_counter > 50:   
                    print('go backwards')
                    Rover.brake = 0
                    Rover.throttle = -Rover.throttle_set*2
                    Rover.steer = random()*30*15
                    if Rover.vel < -Rover.max_vel/2:  
                        Rover.throttle = 0
                        Rover.brake = Rover.brake_set*2
                        time.sleep(2)
                        Rover.brake = 0
                        Rover.throttle = 0
                        Rover.loop_counter = 0
                        Rover.mode = 'stop'
                            
                if Rover.loop_counter > 80:
                    Rover.throttle_set = 0
                    Rover.brake = Rover.brake_set*2
                    time.sleep(2)
                    Rover.brake = 0
                    Rover.throttle_set = 0
                    Rover.steer = 15
                         
                if Rover.loop_counter > 86:
                    Rover.brake = 0
                    Rover.throttle_set = 0
                    Rover.steer = 0
                    Rover.loop_counter = 0
                    Rover.mode = 'stop'                        
                
            else:
                Rover.loop_counter = 0        

        # After rover has picked-up sample, go backwards a bit
        elif Rover.samples_found > Rover.prev_samples_found or Rover.mode == 'backward':
            #print(Rover.samples_found)
            #print(Rover.prev_samples_found)
            Rover.loop_counter3 += 1
            Rover.mode = 'backward'
            Rover.prev_samples_found = Rover.samples_found
            Rover.brake = 0
            Rover.throttle = -Rover.throttle_set
            Rover.steer += 2
        
            if Rover.vel < -Rover.max_vel/2 or Rover.loop_counter3 > 60:         
                Rover.brake = Rover.brake_set*2
                time.sleep(2)
                Rover.brake = 0
                Rover.throttle = Rover.throttle_set
                #Rover.steer = np.clip(np.percentile(Rover.nav_angles * 180/np.pi,35), -15, 12)
                Rover.mode = 'stop'
                Rover.loop_counter3 = 0


    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None and Rover.mode is not 'pick-up':
        
        if  (abs(Rover.roll) >= 4 and abs(Rover.roll) <= 360-4) or abs(Rover.pitch) >= 4 and abs(Rover.pitch) <= 360-4:
            Rover.mode = 'stop'
   
        # Check for Rover.mode status
        if Rover.mode == 'forward': 
            # Check the extent of navigable terrain
            
            if len(np.clip(Rover.nav_angles,-15,15)) > Rover.stop_forward:         
            # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if abs(Rover.vel) < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                    Rover.brake = 0
                else: # Else coast
                    Rover.throttle = 0
                    Rover.brake = 0
                    
                if abs(Rover.vel) > Rover.max_vel*1.5:
                    Rover.brake = Rover.brake_set
                if abs(Rover.vel) > Rover.max_vel*2:
                    Rover.brake = Rover.brake_set*2    
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.percentile(Rover.nav_angles * 180/np.pi,38), -15, 12)
                
                #If rover is stuck, initiate the following procedure
                if Rover.vel < 0.2 and Rover.throttle == Rover.throttle_set:
                    Rover.loop_counter += 1
                    if Rover.loop_counter > 30:
                        print('stuck')
                        Rover.steer = random()*30-15
                        Rover.brake = 0
                        Rover.throttle = Rover.throttle_set*2
                        time.sleep(0.5)
                        if Rover.vel > Rover.max_vel/2:  
                            Rover.throttle = 0
                            Rover.brake = Rover.brake_set*2
                            time.sleep(2)
                            Rover.brake = 0
                            Rover.throttle = 0
                            Rover.loop_counter = 0
                            Rover.mode = 'stop'
                                                                        
                    if Rover.loop_counter > 50:   
                        print('go backwards')
                        Rover.brake = 0
                        Rover.throttle = -Rover.throttle_set*2
                        Rover.steer = random()*30*15
                        if Rover.vel < -Rover.max_vel/3:  
                            Rover.throttle = 0
                            Rover.brake = Rover.brake_set*2
                            time.sleep(2)
                            Rover.brake = 0
                            Rover.throttle = 0
                            Rover.loop_counter = 0
                            Rover.mode = 'stop'
                            
                    if Rover.loop_counter > 70:
                         Rover.throttle_set = 0
                         Rover.brake = Rover.brake_set*2
                         time.sleep(2)
                         Rover.brake = 0
                         Rover.throttle_set = 0
                         Rover.steer = 15
                         
                    if Rover.loop_counter > 76:
                        Rover.brake = 0
                        Rover.throttle_set = 0
                        Rover.steer = 0
                        Rover.loop_counter = 0
                        Rover.mode = 'stop'                        
                
                else:
                    Rover.loop_counter = 0 
                    
                # Detect if steering is stuck    
                if abs(Rover.steer) > 9 or (round(Rover.pos[0],1),round(Rover.pos[1],1)) == (round(Rover.prev_pos[0],1),round(Rover.prev_pos[1],1)):
                    # Upodate counter
                    Rover.loop_counter2 += 1
                    # Check if duration of turining has persisted for 50 clicks
                    if Rover.loop_counter2 > 150:
                        # Update Rover.mode so it can be handled subsequently
                        Rover.steer = -np.clip(np.percentile(Rover.nav_angles * 180/np.pi,39), -15, 12)
                        time.sleep(2)
                        Rover.mode = 'stop'
                        # Re-set counter
                        Rover.loop_counter2 = 0
                        print('stuck-turning-position')
                else:
                    # Re-set counter
                    Rover.loop_counter2 = 0
   
                        
                    
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            else: #len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            
            # If we're in stop mode but still moving keep braking
            if abs(Rover.vel) > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                #if not reduce(np.logical_or,(len(Rover.nav_angles) >= Rover.stop_forward, Rover.center_dist > 110,  Rover.center_dist < 70)):
                Rover.throttle = 0
                # Release the brake to allow turning
                Rover.brake = 0
                # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                Rover.steer = 15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(np.clip(Rover.nav_angles,-15,15)) > Rover.stop_forward:
                    # Set throttle back to stored value
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.percentile(Rover.nav_angles * 180/np.pi,39), -15, 12)
                    Rover.mode = 'forward'
                    Rover.throttle = Rover.throttle_set
                    time.sleep(0.3)
                    
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    elif Rover.mode is not 'pick-up':

        Rover.steer = 0
        Rover.brake = 0
        Rover.mode ='forward'
        

        
    Rover.prev_pos = Rover.pos
    print(Rover.mode)
    return Rover


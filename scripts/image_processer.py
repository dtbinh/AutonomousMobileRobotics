#!/usr/bin/env python

import rospy
import cv2 
import numpy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import String
from geometry_msgs.msg import Twist 

class image_converter:

    def __init__(self):

        cv2.namedWindow("Image window", 1)
        cv2.namedWindow("Thresh", 1)
        self.bridge = CvBridge()
        cv2.startWindowThread()
        self.image_sub = rospy.Subscriber("/turtlebot_1/camera/rgb/image_raw",Image,self.callback)
        self.image_mean_pub = rospy.Publisher("/turtlebot_1/camera/hsv_mean", String)
        self.motion_pub = rospy.Publisher("/turtlebot_1/cmd_vel", Twist)
    
    def callback(self, data):
        cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        hsv_img = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        pub_string = "H: " + repr(numpy.mean(hsv_img[:, :, 0])) + "\nS: " + repr(numpy.mean(hsv_img[:, :, 1])) + "\nV: " + repr(numpy.mean(hsv_img[:, :, 2]))
                                    
        print(pub_string + "\n---------------------")
        self.image_mean_pub.publish(pub_string)
                            
        # define range of blue color in HSV
        green_min = numpy.array([50,150,50])
        green_max = numpy.array([255,255,255])
    
        # Threshold the HSV image to get only blue colors
        mask_img = cv2.inRange(hsv_img, green_min, green_max)
        h, w, d = mask_img.shape
        top_cutoff = h - (h / 3)
        bottom_cutoff = h + (h / 3)
        
        mask_img[0:top_cutoff, 0:w] = 0
        mask_img[0:bottom_cutoff, 0:w] = 0
        
        if(mask_img.sum() >= 1):
            M = cv2.moments(mask_img)
            
            if M['m00'] > 0:
              cx = int(M['m10']/M['m00'])
              cy = int(M['m01']/M['m00'])
              
            base_cmd = Twist()
            base_cmd.linear.x = base_cmd.linear.y = base_cmd.angular.z = 0;  
            err = cx - w/2
            self.twist.linear.x = 0.2
            self.twist.angular.z = -float(err) / 100
                
            self.motion_pub.publish(base_cmd)
            
        # Bitwise-AND mask and original image
        original_masked = cv2.bitwise_and(cv_image, cv_image, mask=mask_img)
        cv2.imshow("Image window", cv_image)
        cv2.imshow("Thresh", original_masked)

rospy.init_node('image_converter')
ic = image_converter()
rospy.spin()

cv2.destroyAllWindows()
#!/usr/bin/env python
import rospy
from geometry_msgs.msg  import Twist
from nav_msgs.msg import Odometry
from math import pow,atan2,sqrt,sin,cos
from tf.transformations import euler_from_quaternion, quaternion_from_euler
import numpy as np 

class turtlebot():

    def __init__(self):
        #Creating our node,publisher and subscriber
        rospy.init_node('turtlebot_controller', anonymous=True)
        self.velocity_publisher = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=10)
        self.pose_subscriber = rospy.Subscriber('/odom', Odometry, self.callback)
        self.pose = Odometry()
        self.rate = rospy.Rate(10)

    #Callback function implementing the pose value received
    def callback(self, data):
        self.pose = data.pose.pose.position
        self.orient = data.pose.pose.orientation
        self.pose.x = round(self.pose.x, 4)
        self.pose.y = round(self.pose.y, 4)

    def get_distance(self, goal_x, goal_y):
        distance = sqrt(pow((goal_x - self.pose.x), 2) + pow((goal_y - self.pose.y), 2))
        return distance

    def move2goal(self):
        goal_pose_ = Odometry()
        goal_pose = goal_pose_.pose.pose.position
        goal_pose.x = input("Set your x goal:")
        goal_pose.y = input("Set your y goal:")
        distance_tolerance = input("Set your tolerance:")
        vel_msg = Twist()
        r = sqrt(pow((goal_pose.x - self.pose.x), 2) + pow((goal_pose.y - self.pose.y), 2))
        while r >= distance_tolerance:

            #Proportional Controller
            #linear velocity in the x-axis:
            r = sqrt(pow((goal_pose.x - self.pose.x), 2) + pow((goal_pose.y - self.pose.y), 2))
            psi = atan2(goal_pose.y - self.pose.y, goal_pose.x - self.pose.x)
            orientation_list = [self.orient.x, self.orient.y, self.orient.z, self.orient.w]
            (roll, pitch, yaw) = euler_from_quaternion (orientation_list)
            theta = yaw
            phi = theta - psi
            if phi > np.pi:
                phi = phi - 2*np.pi
            if phi < -np.pi:
                phi = phi + 2*np.pi

            vel_msg.linear.x = 0.3*r*cos(phi)
            vel_msg.linear.y = 0
            vel_msg.linear.z = 0

            #angular velocity in the z-axis:
            vel_msg.angular.x = 0
            vel_msg.angular.y = 0
            vel_msg.angular.z = -0.3*sin(phi)*cos(phi)-(0.4*phi)

            #Publishing our vel_msg
            print(self.pose.x)
            print(self.pose.y)
            print(r)
            self.velocity_publisher.publish(vel_msg)
            self.rate.sleep()
        #Stopping our robot after the movement is over
        vel_msg.linear.x = 0
        vel_msg.angular.z =0
        self.velocity_publisher.publish(vel_msg)

if __name__ == '__main__':
   x = turtlebot()
   while 1:
      try:
       	#Testing our function
        x.move2goal()
      except rospy.ROSInterruptException: pass

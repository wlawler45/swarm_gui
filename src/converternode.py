#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy

class talker:
    def __init__(self):
        self.pub = rospy.Publisher('/bluetooth_teleop/joy', Joy, queue_size=10)
        
        self.ridgeback_vel_msg = Joy()
        '''
        ridgeback_vel_msg.linear.x = 0
        ridgeback_vel_msg.linear.y = 0
        ridgeback_vel_msg.linear.z = 0
        ridgeback_vel_msg.angular.x = 0
        ridgeback_vel_msg.angular.y = 0
        ridgeback_vel_msg.angular.z = 0
        '''
        self.pub.publish(self.ridgeback_vel_msg)
        rospy.sleep(0.25)
        
        rospy.Subscriber("/spacenav/twist/repub", Twist, self.callback)

    def callback(self,data):
        vx = data.linear.x
        vy = data.linear.y
        wz = data.angular.z
        
        self.ridgeback_vel_msg.buttons = [0]*15
        self.ridgeback_vel_msg.axes = [0]*6
        
        self.ridgeback_vel_msg.buttons[4] = 1

        self.ridgeback_vel_msg.axes[0] = -vy*0.5
        self.ridgeback_vel_msg.axes[1] = -vx*0.5
        self.ridgeback_vel_msg.axes[3] = wz*0.5
        self.ridgeback_vel_msg.axes[5] = 1.0

        print(self.ridgeback_vel_msg)
        self.pub.publish(self.ridgeback_vel_msg)
        #while not rospy.is_shutdown():
        
            
            

if __name__ == '__main__':
    rospy.init_node('listener', anonymous=True)
    talker()
    

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


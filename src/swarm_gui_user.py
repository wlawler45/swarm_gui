#!/usr/bin/env python
import os
import rospy
import rospkg
import collections
import time
import sys
import subprocess
import numpy as np
from qt_gui.plugin import Plugin
#from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget, QDialog
from python_qt_binding.QtCore import QMutex, QMutexLocker,QSemaphore, QThread
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, uic
import threading
from geometry_msgs.msg import Pose2D, Twist
from led_indicator import LEDIndicator
import rosnode

callback_lock=threading.Lock()

    
#class robot_button(QtWidgets.QPushButton):
class robot_button:
    def __init__(self,number,topic):
        
        self.text="Robot "+str(number+1)+" Motion Enable"
        self.enabled=False
        
        self.button=QPushButton()
        self.button.setText(self.text)
        self.button.pressed.connect(self.button_pressed)
        self.publisher=rospy.Publisher(topic, Twist, queue_size=10)
    def button_pressed(self):
        self.enabled=not(self.enabled)
        
        if(self.enabled):
            
            self.button.setStyleSheet('QPushButton {background-color: orange; color: white;}')
            
        else:
            
            self.button.setStyleSheet('QPushButton {background-color: white; color: black;}')
    
class LEDManager:
    def __init__(self,nodenames,led_objects):
        self.nodenames=nodenames
        self.led_objects=led_objects
    def poll_node_names(self):
        #nodenames is loaded from yaml file and should be a list of lists for each robot of desired nodes
        #print(self.nodenames)
        for i in range(len(self.nodenames)):
            current_status=True
            for nodename in self.nodenames[i]:
                #print(nodename)
                if(nodename not in rosnode.get_node_names()):
                    #print(nodename)
                    current_status=False
                    break
            
            #print("end")
            #print(current_status)
            self.led_objects[i].led_change(current_status)
            #time.sleep(0.01)
            
class SWARMGUI(QtWidgets.QMainWindow):

    def __init__(self):
        super(SWARMGUI, self).__init__()
        
        self.setObjectName('MyPlugin')
        self.synced_control_enabled=False
        self.mainscreenui = os.path.join(rospkg.RosPack().get_path('swarm_gui'), 'resource', 'mainwindow.ui')
        uic.loadUi(self.mainscreenui, self)
        
        self.Syncmotions.pressed.connect(self.sync_robot_motion_pressed)
        #self.Robot1enable.pressed.connect(self.rob1enable)
        #self.Robot2enable.pressed.connect(self.rob2enable)
        #self.Robot3enable.pressed.connect(self.rob3enable)
        #self.rob1en=False
        #self.rob2en=False
        #self.rob3en=False
        
        #self.pub1=rospy.Publisher('/spacenav/twist/repub', Twist, queue_size=10)
        #self.pub3=rospy.Publisher('/spacenav/twist/repub3', Twist, queue_size=10)
        #self.pub2=rospy.Publisher('/spacenav/twist/repub2', Twist, queue_size=10)
        self.show()
        
        #rospy.Subscriber("/OARBOT1/pose", Pose2D, callback) 
        
        self.Leds=[]

        #self.number_of_bots=3
        #self.number_of_bots=rospy.get_param('number_of_robots')
        try:
            self.number_of_bots=rospy.get_param('number_of_robots')
            self.nodenames=rospy.get_param('robot_node_names')
            self.command_topics=rospy.get_param('command_topics')
            self.input_command_topic=rospy.get_param('input_command_topic')
        except:
            self.number_of_bots=4
            self.nodenames=[["/rosout"],["hello"],["hello"]]
            self.command_topics=["/spacenav/twist/repub","/spacenav/twist/repub2","/spacenav/twist/repub3","hello"]
            self.input_command_topic='spacenav/twist'

        rospy.Subscriber(self.input_command_topic, Twist, self.offset_callback)
        for i in range(self.number_of_bots):
            led=LEDIndicator()
            led.setDisabled(True)
            self.Robotlayout.addWidget(led,1,i)
            self.Leds.append(led)
	
        self.status_manager=LEDManager(self.nodenames,self.Leds)
        self.buttons=[]
        for i in range(self.number_of_bots):
            if(len(self.command_topics) != self.number_of_bots):
                print("NOT ENOUGH COMMAND TOPICS GIVEN FOR NUMBER OF ROBOTS")
                break
            button_class_object=robot_button(i,self.command_topics[i])
            self.Robotlayout.addWidget(button_class_object.button,0,i)
            self.buttons.append(button_class_object)

        """
        self.robot1led=LEDIndicator()
        self.robot1led.setDisabled(True)
        self.robot2led=LEDIndicator()
        self.robot2led.setDisabled(True)
        self.robot3led=LEDIndicator()
        self.robot3led.setDisabled(True)
        
        self.Robotlayout.addWidget(self.robot1led,1,0)
        self.Robotlayout.addWidget(self.robot2led,1,1)
        self.Robotlayout.addWidget(self.robot3led,1,2)
        """
        rospy.Timer(rospy.Duration(0.1), self.callback_gui)
        #needed_robot_nodes=[]
        self.plus = os.path.join(rospkg.RosPack().get_path('swarm_gui'), 'resource', '+.PNG')
        self.minus = os.path.join(rospkg.RosPack().get_path('swarm_gui'), 'resource', '-.PNG')
        icon=QIcon()
        icon.addPixmap(QPixmap(self.plus))
        self.plusbutton.setIcon(icon)
        self.plusbutton.setIconSize(QSize(100,100))
        icon2=QIcon()
        icon2.addPixmap(QPixmap(self.minus))
        self.minusbutton.setIcon(icon2)
        self.minusbutton.setIconSize(QSize(100,100))
    
    
   
    def callback_gui(self,evt):
        self.status_manager.poll_node_names()
        """
        for node_name in rosnode.get_node_names():
            print(node_name)
        if('/rosout' in rosnode.get_node_names()):
            self.robot1led.led_change(True)
        else:
            self.robot1led.led_change(False)
        """
    def offset_callback(self,data):
        with(callback_lock):
            
            
            for i in range(len(self.buttons)):
                if(self.buttons[i].enabled):
                    self.buttons[i].publisher.publish(data)
           
    
            


    def sync_robot_motion_pressed(self):
        for i in range(len(self.buttons)):
            self.synced_control_enabled=True
            if(not self.buttons[i].enabled):
                self.synced_control_enabled=False
                break
                
        #if(self.rob1en and self.rob2en and self.rob3en): self.synced_control_enabled=True
        self.synced_control_enabled=not(self.synced_control_enabled)
        
        if(self.synced_control_enabled):
            for i in range(len(self.buttons)):
                self.buttons[i].enabled=True
                self.buttons[i].button.setStyleSheet('QPushButton {background-color: orange; color: white;}')
            
            
        else:
            for i in range(len(self.buttons)):
                self.buttons[i].enabled=False
                self.buttons[i].button.setStyleSheet('QPushButton {background-color: white; color: black;}')
            
            
    #def motion_callback(self):
        
    

def main():
    rospy.init_node('SWARM_gui')
    app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
    window = SWARMGUI() # Create an instance of our class
    app.exec_() # Start the application

if __name__== '__main__':
    main()


#!/usr/bin/env python

import rospy
import tf
from geometry_msgs.msg import PointStamped
from nav_msgs.msg import Odometry
from crazyflie_driver.srv import UpdateParams

def onNewTransform(odom):
    global msg
    global pub
    global firstTransform

    if firstTransform:
        # initialize kalman filter
        rospy.set_param("kalman/initialX", odom.pose.pose.position.x)
        rospy.set_param("kalman/initialY", odom.pose.pose.position.y)
        rospy.set_param("kalman/initialZ", odom.pose.pose.position.z)
        update_params(["kalman/initialX", "kalman/initialY", "kalman/initialZ"])
        rospy.set_param("kalman/resetEstimation", 1)
        update_params(["kalman/resetEstimation"])
        firstTransform = False
    else:
        msg.header.frame_id = odom.header.frame_id
        msg.header.stamp = odom.header.stamp
        msg.header.seq += 1
        msg.point.x = odom.pose.pose.position.x
        msg.point.y = odom.pose.pose.position.y
        msg.point.z = odom.pose.pose.position.z
        pub.publish(msg)


if __name__ == '__main__':
    rospy.init_node('publish_external_position_vicon', anonymous=True)
    topic = rospy.get_param("~topic", "/vicon/cf/cf")

    rospy.wait_for_service('update_params')
    rospy.loginfo("found update_params service")
    update_params = rospy.ServiceProxy('update_params', UpdateParams)

    firstTransform = True

    msg = PointStamped()
    msg.header.seq = 0
    msg.header.stamp = rospy.Time.now()

    pub = rospy.Publisher("external_position", PointStamped, queue_size=1)
    rospy.Subscriber(topic, Odometry, onNewTransform)

    rospy.spin()
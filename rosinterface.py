# import module for ROS.
# Provides a wrapper around the rosbee hardware abstraction module
# Opteq febr 2016

import rbha.py

# Disable of robot
def disable_robot():
    rbha.disable_robot()

# Enable of robot
def enable_robot():
    rbha.enable_robot()

# request robot enable status. Returns true if enabled and false if disabled
def request_enable_status():
    return rbha.request_enable_status()

# request alarm bit status of robot. Returns true if any alarm set
def request_alarm():
    return rbha.request_alarm()

# Get actual move speed and rotational speed of robot in SI units
# Reports calculated speed x from motor encoders and robot rotation based on either encoders of gyro depending on gyrobased being true
def get_movesteer(gyrobased):
    return rbha.get_movesteer(gyrobased)

# Move command. Input in SI units. speed in m/s dir in radians per sec
def do_movesteer(speed, rot_z):
    rbha.do_movesteer(speed, rot_z)


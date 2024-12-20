#!/bin/bash
set -e

# Source the ROS setup
source /opt/ros/noetic/setup.bash

# Pull the latest updates from the repositories
cd /root/catkin_ws/src
if [ -d "cnmpc_recording" ]; then
    cd cnmpc_recording && git pull && cd ..
else
    git clone git@github.com:achilleas2942/cnmpc_recording.git
fi

# Build the workspace
cd /root/catkin_ws/
catkin_make
cd /

# Source the workspace
source /root/catkin_ws/devel/setup.bash

# Run the command passed in the Kubernetes pod spec or default to running the metrics script
python3 /root/catkin_ws/src/cnmpc_recording/src/k8s_resource_metrics.py

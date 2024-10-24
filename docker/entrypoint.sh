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

# Make run_k8s_resource_metrics.sh executable
chmod +x /root/catkin_ws/src/cnmpc_recording/src/run_k8s_resource_metrics.sh

# Execute the provided command
exec "$@"

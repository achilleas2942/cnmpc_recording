#!/usr/bin/env python

import rospy
import subprocess
from std_msgs.msg import String

def get_k8s_pod_metrics():
    """Gets CPU and memory usage of Kubernetes pods using kubectl."""
    try:
        # Execute kubectl top pods command
        result = subprocess.check_output(["kubectl", "top", "pods"], universal_newlines=True)
        return result
    except subprocess.CalledProcessError as e:
        rospy.logerr(f"Error getting pod metrics: {e}")
        return None

def get_k8s_node_metrics():
    """Gets CPU and memory usage of Kubernetes nodes using kubectl."""
    try:
        # Execute kubectl top nodes command
        result = subprocess.check_output(["kubectl", "top", "nodes"], universal_newlines=True)
        return result
    except subprocess.CalledProcessError as e:
        rospy.logerr(f"Error getting node metrics: {e}")
        return None

def parse_k8s_pod_metrics(metrics):
    """Parses the pod metrics and extracts CPU and memory usage."""
    pod_data = []
    lines = metrics.splitlines()[1:]  # Skip the header row
    for line in lines:
        parts = line.split()
        pod_name = parts[0]
        cpu_usage = parts[1]
        memory_usage = parts[2]
        pod_data.append(f"{pod_name}: CPU={cpu_usage}, Memory={memory_usage}")
    return pod_data

def parse_k8s_node_metrics(metrics):
    """Parses the node metrics and extracts CPU and memory usage."""
    node_data = []
    lines = metrics.splitlines()[1:]  # Skip the header row
    for line in lines:
        parts = line.split()
        node_name = parts[0]
        cpu_usage_cores = parts[1]
        cpu_usage_percent = parts[2]
        memory_usage_bytes = parts[3]
        memory_usage_percent = parts[4]
        node_data.append(f"{node_name}: CPU={cpu_usage_cores} cores ({cpu_usage_percent}%), Memory={memory_usage_bytes} bytes ({memory_usage_percent}%)")
    return node_data

def k8s_resource_monitor():
    """ROS node to monitor and publish Kubernetes resource usage metrics."""
    # Initialize the ROS node
    rospy.init_node('k8s_resource_monitor', anonymous=True)

    # Create ROS publishers
    pod_pub = rospy.Publisher('/k8s_pod_metrics', String, queue_size=10)
    node_pub = rospy.Publisher('/k8s_node_metrics', String, queue_size=10)

    # Define rate for the loop (1Hz)
    rate = rospy.Rate(1)

    while not rospy.is_shutdown():
        # Get pod and node metrics
        pod_metrics = get_k8s_pod_metrics()
        node_metrics = get_k8s_node_metrics()

        if pod_metrics:
            # Parse and publish pod metrics
            parsed_pod_metrics = parse_k8s_pod_metrics(pod_metrics)
            for pod_metric in parsed_pod_metrics:
                rospy.loginfo(f"Pod Metric: {pod_metric}")
                pod_pub.publish(pod_metric)

        if node_metrics:
            # Parse and publish node metrics
            parsed_node_metrics = parse_k8s_node_metrics(node_metrics)
            for node_metric in parsed_node_metrics:
                rospy.loginfo(f"Node Metric: {node_metric}")
                node_pub.publish(node_metric)

        # Sleep to maintain loop rate
        rate.sleep()

if __name__ == '__main__':
    try:
        k8s_resource_monitor()
    except rospy.ROSInterruptException:
        pass

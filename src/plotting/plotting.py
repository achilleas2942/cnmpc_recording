import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from extract_data_to_dict import extract_data_to_dict
from bagpy import bagreader
from scipy.signal import medfilt
from scipy.interpolate import interp1d


def call_main():
    # Load the bag file
    bag_file = "/home/oem/Downloads/testing5.bag"
    b = bagreader(bag_file)

    # List of topics to read from the bag file
    topic_list = [
        "/av_downlink",
        "/downlink_delay",
        "/av_uplink",
        "/uplink_delay",
        "/solver_time",
        "/av_rtt",
        "/equilibrium_resources",
        "/time_resources",
        "/time_error",
        "/k8s_node_metrics",
        "/k8s_pod_metrics",
    ]

    # Initialize dictionaries to store data for each topic
    data_storage = {topic: {} for topic in topic_list}

    # Extract data for each topic
    for topic in topic_list:
        topic_data = b.message_by_topic(topic)
        data = pd.read_csv(topic_data)

        # Print the columns of the DataFrame to understand its structure
        print(f"Columns for topic {topic}: {data.columns}")

        if topic == "/av_downlink":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/downlink_delay":
            data_storage[topic] = extract_data_to_dict(
                data, ["Time", "stamp.secs", "stamp.nsecs"]
            )
        elif topic == "/av_uplink":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/uplink_delay":
            data_storage[topic] = extract_data_to_dict(
                data, ["Time", "stamp.secs", "stamp.nsecs"]
            )
        elif topic == "/av_rtt":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/equilibrium_resources":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/time_resources":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/time_error":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/k8s_node_metrics":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/k8s_pod_metrics":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/solver_time":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])

    if "/av_downlink" in data_storage:
        av_downlink = data_storage["/av_downlink"]
        time_avd = av_downlink["Time"]
        av_downlink = np.array(list(zip(av_downlink["data"])))

    if "/av_uplink" in data_storage:
        av_uplink = data_storage["/av_uplink"]
        time_avu = av_uplink["Time"]
        av_uplink = np.array(list(zip(av_uplink["data"])))

    if "/solver_time" in data_storage:
        solver_time = data_storage["/solver_time"]
        time_s = solver_time["Time"]
        solver_time = np.array(solver_time["data"]) * 1e-3

    if "/av_rtt" in data_storage:
        av_rtt = data_storage["/av_rtt"]
        av_rtt = np.array(list(zip(av_rtt["data"])))

    # Interpolate av_downlink, av_uplink, and solver_time to a common time base
    min_time = max(time_avd[0], time_avu[0], time_s[0])  # Start at the max of start times
    max_time = min(time_avd[-1], time_avu[-1], time_s[-1])  # End at the min of end times

    # Define a common time base with a chosen frequency
    common_time = np.linspace(min_time, max_time, min(len(time_avd), len(time_avu), len(time_s)))

    # Interpolate each dataset to the common time base
    av_downlink_interp = interp1d(time_avd, av_downlink, kind="linear", fill_value="extrapolate")(common_time)
    av_uplink_interp = interp1d(time_avu, av_uplink, kind="linear", fill_value="extrapolate")(common_time)
    solver_time_interp = interp1d(time_s, solver_time, kind="linear", fill_value="extrapolate")(common_time)

    # Calculate Round Trip Time (RTT)
    round_trip_time = av_downlink_interp + av_uplink_interp + solver_time_interp

    if "/equilibrium_resources" in data_storage:
        equilibrium_resources = data_storage["/equilibrium_resources"]
        equilibrium_resources = np.array(list(zip(equilibrium_resources["data"])))

    if "/time_resources" in data_storage:
        time_resources = data_storage["/time_resources"]
        time_resources = np.array(list(zip(time_resources["data"])))

    if "/time_error" in data_storage:
        time_error = data_storage["/time_error"]
        time_error = np.array(list(zip(time_error["data"])))

    if "/k8s_node_metrics" in data_storage:
        k8s_node_metrics = data_storage["/k8s_node_metrics"]
        k8s_node_metrics = np.array(list(zip(k8s_node_metrics["data"])))

    if "/k8s_pod_metrics" in data_storage:
        k8s_pod_metrics = data_storage["/k8s_pod_metrics"]
        k8s_pod_metrics = np.array(list(zip(k8s_pod_metrics["data"])))

    if "/downlink_delay" in data_storage:
        downlink_delay = data_storage["/downlink_delay"]
        time_d = downlink_delay["Time"]
        downlink_delay = np.array(downlink_delay["stamp.nsecs"]) * 1e-9

    if "/uplink_delay" in data_storage:
        uplink_delay = data_storage["/uplink_delay"]
        time_u = uplink_delay["Time"]
        uplink_delay = np.array(uplink_delay["stamp.nsecs"]) * 1e-9

    # Plotting
    with plt.style.context(["science", "ieee"]):
        # Plot Downlink delay
        plt.figure()
        plt.plot(time_d, downlink_delay, color="red", alpha=0.6, label="average")
        plt.plot(time_avd, av_downlink, color="red", label="downlink delay")
        plt.ylabel("(a) Downlink delay (s)", fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # Plot Uplink delay
        plt.figure()
        plt.plot(time_u, uplink_delay, color="red", alpha=0.6, label="average")
        plt.plot(time_avu, av_uplink, color="red", label="downlink delay")
        plt.ylabel("(a) Uplink delay (s)", fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # Plot Solver time
        plt.figure()
        plt.plot(time_s, solver_time, color="red", label="average")
        plt.ylabel("(a) Solver time (s)", fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # Plot Round-trip time
        plt.figure()
        plt.plot(common_time, round_trip_time, color="red", label="average")
        plt.ylabel("(a) Round trip time (s)", fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(True)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    try:
        call_main()
    except (RuntimeError, TypeError, NameError) as e:
        print("OOPS ERROR OCCURRED:", e)

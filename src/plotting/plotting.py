import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from extract_data_to_dict import extract_data_to_dict
from bagpy import bagreader
from scipy.signal import medfilt
from scipy.interpolate import interp1d


window_size = 1000

# Function to compute the sliding window average
def sliding_window_average(data, window_size):
    averages = []
    window = []

    for value in data:
        window.append(value)
        if len(window) > window_size:
            window.pop(0)  # Remove the oldest value to keep the window size constant
        if len(window) == window_size:
            averages.append(sum(window) / window_size)
        else:
            averages.append(np.nan)  # To keep the array lengths the same, append NaN for initial values
    return averages

def clean_data(time_array, data_array):
    # Ensure arrays are 1D and convert to float
    time_array = np.asarray(time_array, dtype=float).ravel()
    data_array = np.asarray(data_array, dtype=float).ravel()
    
    # Mask to keep only finite values in both arrays
    mask = np.isfinite(time_array) & np.isfinite(data_array)
    
    # Return only valid (finite) data points
    return time_array[mask], data_array[mask]

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

    try:
        time_avd, av_downlink = clean_data(time_avd, av_downlink)
        time_avu, av_uplink = clean_data(time_avu, av_uplink)
        time_s, solver_time = clean_data(time_s, solver_time)
    except Exception as e:
        print("Error during data cleaning:", e)
        return

    # Define a common time base
    min_time = float(max(time_avd[0], time_avu[0], time_s[0]))
    max_time = float(min(time_avd[-1], time_avu[-1], time_s[-1]))
    num_points = min(len(time_avd), len(time_avu), len(time_s))

    common_time = np.linspace(min_time, max_time, num_points)

    av_downlink_interp = interp1d(time_avd, av_downlink, kind="linear", fill_value="extrapolate")(common_time)
    av_uplink_interp = interp1d(time_avu, av_uplink, kind="linear", fill_value="extrapolate")(common_time)
    solver_time_interp = interp1d(time_s, solver_time, kind="linear", fill_value="extrapolate")(common_time)
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

    solver_time_avg = sliding_window_average(solver_time, window_size)
    round_trip_time_avg = sliding_window_average(round_trip_time, window_size)

    # Plotting
    with plt.style.context(["science", "ieee"]):
        fig, axs = plt.subplots(4, 1, figsize=(8, 12), sharex=True)  # 4 rows, 1 column, shared x-axis

        # Plot Downlink delay
        axs[0].plot(time_d, downlink_delay, color="red", alpha=0.6, label="average")
        axs[0].plot(time_avd, av_downlink, color="red", label="downlink delay")
        axs[0].set_ylabel("Downlink delay (s)", fontsize=12)
        # axs[0].legend(loc="upper right")
        axs[0].grid(True)

        # Plot Uplink delay
        axs[1].plot(time_u, uplink_delay, color="blue", alpha=0.6, label="average")
        axs[1].plot(time_avu, av_uplink, color="blue", label="uplink delay")
        axs[1].set_ylabel("Uplink delay (s)", fontsize=12)
        # axs[1].legend(loc="upper right")
        axs[1].grid(True)

        # Plot Solver time
        axs[2].plot(time_s, solver_time, color="green", alpha=0.6, label="average")
        axs[2].plot(time_s, solver_time_avg, color="green", label="solver time")
        axs[2].set_ylabel("Solver time (s)", fontsize=12)
        # axs[2].legend(loc="upper right")
        axs[2].grid(True)

        # Plot Round-trip time
        axs[3].plot(common_time, round_trip_time, color="black", alpha=0.6, label="average")
        axs[3].plot(common_time, round_trip_time_avg, color="black", label="round trip time")
        axs[3].set_ylabel("Round trip time (s)", fontsize=12)
        # axs[3].legend(loc="upper right")
        axs[3].grid(True)

        # Set common x-axis label
        axs[3].set_xlabel("Time (s)", fontsize=12)
        
        # Adjust layout for tight spacing
        plt.tight_layout()
        plt.show()



if __name__ == "__main__":
    try:
        call_main()
    except (RuntimeError, TypeError, NameError) as e:
        print("OOPS ERROR OCCURRED:", e)

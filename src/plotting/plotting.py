import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from extract_data_to_dict import extract_data_to_dict
from bagpy import bagreader
from scipy.signal import medfilt
from scipy.interpolate import interp1d


# Function to compute the sliding window average
def sliding_window_average(data):
    averages = []
    window = []

    for value in data:
        window.append(value)
        if len(window) > 1000:
            window.pop(0)  # Remove the oldest value to keep the window size constant
        if len(window) == 1000:
            averages.append(sum(window) / 1000)
        else:
            averages.append(
                sum(window) / len(window)
            )  # To keep the array lengths the same, append NaN for initial values
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
        av_downlink = np.array(av_downlink["data"]) + 0.010

    if "/av_uplink" in data_storage:
        av_uplink = data_storage["/av_uplink"]
        time_avu = av_uplink["Time"]
        av_uplink = np.array(av_uplink["data"]) - 0.010

    if "/solver_time" in data_storage:
        solver_time = data_storage["/solver_time"]
        time_s = solver_time["Time"]
        solver_time = np.array(solver_time["data"]) * 1e-3

    if "/av_rtt" in data_storage:
        av_rtt = data_storage["/av_rtt"]
        av_rtt = np.array(av_rtt["data"])

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

    av_downlink_interp = interp1d(
        time_avd, av_downlink, kind="linear", fill_value="extrapolate"
    )(common_time)
    av_uplink_interp = interp1d(
        time_avu, av_uplink, kind="linear", fill_value="extrapolate"
    )(common_time)
    solver_time_interp = interp1d(
        time_s, solver_time, kind="linear", fill_value="extrapolate"
    )(common_time)
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
        cpu_values = []
        cpu_times = []
        k8s_pod_metrics = data_storage["/k8s_pod_metrics"]
        k8s_time = k8s_pod_metrics["Time"]
        k8s_data = np.array(list(zip(k8s_pod_metrics["data"])))
        for entry, time in zip(k8s_data, k8s_time):
            entry_str = entry[0]
            if "cnmpc-deployment1-5d5c6b757-mjtzg" in entry_str:
                cpu_part = entry_str.split("CPU=")[1].split(",")[0]
                cpu_value = float(cpu_part.replace("m", "")) / 10.0
                cpu_values.append(cpu_value)
                cpu_times.append(time)
        cpu_values_array = np.array(cpu_values)
        cpu_times_array = np.array(cpu_times)

    if "/downlink_delay" in data_storage:
        downlink_delay = data_storage["/downlink_delay"]
        time_d = downlink_delay["Time"]
        downlink_delay = np.array(downlink_delay["stamp.nsecs"]) * 1e-9 + 0.010

    if "/uplink_delay" in data_storage:
        uplink_delay = data_storage["/uplink_delay"]
        time_u = uplink_delay["Time"]
        uplink_delay = np.array(uplink_delay["stamp.nsecs"]) * 1e-9 - 0.010

    solver_time_avg = sliding_window_average(solver_time)
    round_trip_time_avg = sliding_window_average(round_trip_time)

    # Plotting
    with plt.style.context(["science", "ieee"]):
        fig, axs = plt.subplots(4, 1, figsize=(8, 3), sharex=True)

        for ax in axs:
            ax.tick_params(axis='both', labelsize=6)

        # Plot Uplink delay
        axs[0].plot(time_u, uplink_delay, color="blue", alpha=0.5, label="average")
        axs[0].plot(time_avu, av_uplink, color="blue", label="uplink delay")
        axs[0].set_ylim(0.16, 0.4)
        axs[0].set_ylabel("(a) Uplink (s)", fontsize=7)
        axs[0].grid(True)

        # Plot Downlink delay
        axs[1].plot(time_d, downlink_delay, color="red", alpha=0.5, label="average")
        axs[1].plot(time_avd, av_downlink, color="red", label="downlink delay")
        axs[1].set_ylabel("(b) Downlink (s)", fontsize=7)
        axs[1].grid(True)

        # Plot Solver time
        axs[2].plot(time_s, solver_time, color="green", alpha=0.5, label="average")
        axs[2].plot(time_s, solver_time_avg, color="green", label="solver time")
        axs[2].set_ylabel("(c) Solver (s)", fontsize=7)
        axs[2].grid(True)

        # Plot Round-trip time
        axs[3].plot(common_time, round_trip_time, color="black", alpha=0.5, label="average")
        axs[3].plot(common_time, round_trip_time_avg, color="black", label="round trip time")
        axs[3].axhline(y=0.274, color="orange", linestyle="--", label="maximum allowable delay")
        axs[3].set_ylabel("(d) Round trip (s)", fontsize=7)
        axs[3].grid(True)

        # Set common x-axis label
        axs[3].set_xlabel("Time (s)", fontsize=8)

        plt.tight_layout()
        plt.xlim(0, 240)
        plt.savefig("/home/oem/Downloads/control_law.png", bbox_inches="tight")
        plt.show()
        
        # CPU for control law
        plt.plot(cpu_times_array, cpu_values_array, color="black", label="cpu")
        plt.ylabel("CPU (\%)", fontsize=7)
        plt.grid(True)
        plt.tight_layout()
        plt.xlim(0, 240)
        plt.savefig("/home/oem/Downloads/cpu.png", bbox_inches="tight")
        plt.show()


if __name__ == "__main__":
    try:
        call_main()
    except (RuntimeError, TypeError, NameError) as e:
        print("OOPS ERROR OCCURRED:", e)

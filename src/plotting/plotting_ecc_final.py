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
    counter = 0
    counter2 = 0

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
        av_downlink = np.array(av_downlink["data"]) + 0.058

    if "/av_uplink" in data_storage:
        av_uplink = data_storage["/av_uplink"]
        time_avu = av_uplink["Time"]
        av_uplink = np.array(av_uplink["data"]) - 0.09

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
    av_comm_time = av_downlink_interp + av_uplink_interp

    if "/equilibrium_resources" in data_storage:
        equilibrium_resources = data_storage["/equilibrium_resources"]
        equilibrium_resources = np.array(list(zip(equilibrium_resources["data"])))

    if "/time_resources" in data_storage:
        time_resources = data_storage["/time_resources"]
        time_r = np.array(time_resources["Time"])
        time_resources = np.array(time_resources["data"])
        resources = np.zeros(len(time_resources))
        for i in range (0, len(time_resources)-1):
            if time_r[i] < 4.95:
                resources[i] = 1500
                time_resources[i] = 0
        for i in range (0, len(time_resources)-1):
            if time_resources[i] < 3000:
                resources[i] = 1500
            elif time_resources[i] >= 3000 and time_resources[i] <= 5000:
                resources[i] = 3500
            else:
                resources[i] = 6000
        for i in range (0, len(resources)-1):
            counter2 = counter2 + 1
            if resources[i] == 3500:
                resources[i] = 1500
                counter = counter + 1
            if counter > 500:
                break
        for i in range (counter2, len(resources)-1):
            if resources[i] == 3500:
                counter3 = i + 1
                resources[i] = time_resources[counter2]
        for i in range (counter3, len(resources)-1):
            counter4 = i + 1
            if resources[i] == 6000:
                resources[i] = time_resources[counter2]
                counter = counter + 1
            if counter > 1000:
                break
        for i in range (counter4, len(resources)-1):
            resources[i] = time_resources[counter4]
        time_r[len(resources)-1] = 240
        resources[len(resources)-1] = time_resources[counter4]

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
        downlink_delay = np.array(downlink_delay["stamp.nsecs"]) * 1e-9 + 0.058

    if "/uplink_delay" in data_storage:
        uplink_delay = data_storage["/uplink_delay"]
        time_u = uplink_delay["Time"]
        uplink_delay = np.array(uplink_delay["stamp.nsecs"]) * 1e-9 - 0.09

    solver_time_avg = sliding_window_average(solver_time)
    round_trip_time_avg = sliding_window_average(round_trip_time)

    # Define a common time base
    min_time_new = float(max(time_d[0], time_u[0]))
    max_time_new = float(min(time_d[-1], time_u[-1]))
    num_points_new = min(len(time_d), len(time_u))

    common_time_new = np.linspace(min_time_new, max_time_new, num_points_new)

    downlink_interp = interp1d(
        time_d, downlink_delay, kind="linear", fill_value="extrapolate"
    )(common_time_new)
    uplink_interp = interp1d(
        time_u, uplink_delay, kind="linear", fill_value="extrapolate"
    )(common_time_new)
    solver_time_interp_new = interp1d(
        time_s, solver_time, kind="linear", fill_value="extrapolate"
    )(common_time_new)
    comm_time = downlink_interp + uplink_interp
    round_trip_time_new = downlink_interp + uplink_interp + solver_time_interp_new

    # Plotting
    with plt.style.context(["science", "ieee"]):
        fig, axs = plt.subplots(4, 1, figsize=(8, 4.8), sharex=True)

        for ax in axs:
            ax.tick_params(axis='both', labelsize=8)

        # Plot Communication delay
        axs[0].plot(common_time_new, comm_time, color="blue", alpha=0.4, label="average")
        axs[0].plot(common_time, av_comm_time, color="blue", label="uplink delay")
        axs[0].set_ylim(0.12, 0.36)
        axs[0].set_yticks([0.12, 0.24, 0.36])
        axs[0].set_ylabel(r'(a) $\tau_{u}(t)+\tau_{d}(t) \,\, (s)$', fontsize=10)
        axs[0].grid(True)

        # Plot Solver time
        axs[1].plot(time_s, solver_time, color="red", alpha=0.4, label="average")
        axs[1].plot(time_s, solver_time_avg, color="red", label="solver time")
        axs[1].set_ylim(-0.002, 0.06)
        axs[1].set_yticks([0.0, 0.03, 0.06])
        axs[1].set_ylabel(r'(b) $\tau_{r}(t) \,\, (s)$', fontsize=10)
        axs[1].grid(True)

        # Plot Round-trip time
        axs[2].plot(common_time, round_trip_time, color="green", alpha=0.4, label="average")
        axs[2].plot(common_time, round_trip_time_avg, color="green", label="round trip time")
        axs[2].plot(common_time_new, round_trip_time_new, color="green", alpha=0.2, label="average_comm")
        axs[2].axhline(y=0.274, color="orange", linestyle="--", label="maximum allowable delay")
        axs[2].set_ylim(0.14, 0.38)
        axs[2].set_yticks([0.14, 0.22, 0.30, 0.38])
        axs[2].set_ylabel(r'(c) $\tau_{rtt}(t) \,\, (s)$', fontsize=10)
        axs[2].grid(True)
        
        # Plot Resources
        axs[3].plot(time_r, time_resources, color="black", label="resources")
        axs[3].plot(time_r, resources, color="black", linestyle="--", label="actual resources")
        axs[3].fill_between(time_r, 0, resources, color="black", alpha=0.4)
        axs[3].set_ylim(-300, 7500)
        axs[3].set_yticks([0, 2000, 4000, 6000])
        axs[3].set_ylabel(r'(d) $r(t) \,\, (m)$', fontsize=10)
        axs[3].grid(True)

        # Set common x-axis label
        axs[3].set_xlabel(r'Time - $t \,\, (s)$', fontsize=10)

        plt.tight_layout()
        plt.xlim(0, 240)
        plt.xticks([0, 40, 80, 120, 160, 200, 240])
        plt.savefig("/home/oem/Downloads/control_law.pdf", bbox_inches="tight")
        plt.savefig("/home/oem/Downloads/control_law.png", bbox_inches="tight")
        plt.show()


if __name__ == "__main__":
    try:
        call_main()
    except (RuntimeError, TypeError, NameError) as e:
        print("OOPS ERROR OCCURRED:", e)

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
    bag_file = "/home/oem/Downloads/control_law.bag"
    b = bagreader(bag_file)
    counter = 0
    counter2 = 0
    counter3 = 0
    counter4 = 0

    # List of topics to read from the bag file
    topic_list = [
        "/av_downlink",
        "/downlink_delay",
        "/av_solver_time",
        "/solver_time",
        "/av_rtt",
        "/equilibrium_resources",
        "/time_resources",
        "/av_time_error",
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
        elif topic == "/av_rtt":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/equilibrium_resources":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/time_resources":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/av_time_error":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/k8s_node_metrics":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/k8s_pod_metrics":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/solver_time":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])
        elif topic == "/av_solver_time":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])

    if "/av_downlink" in data_storage:
        av_downlink = data_storage["/av_downlink"]
        time_avd = av_downlink["Time"]
        av_downlink = np.array(av_downlink["data"]) + 0.030

    if "/solver_time" in data_storage:
        solver_time = data_storage["/solver_time"]
        time_s = solver_time["Time"]
        solver_time = np.array(solver_time["data"]) * 1e-3

    if "/av_solver_time" in data_storage:
        av_solver_time = data_storage["/av_solver_time"]
        time_avs = av_solver_time["Time"]
        av_solver_time = np.array(av_solver_time["data"])

    if "/av_rtt" in data_storage:
        av_rtt = data_storage["/av_rtt"]
        av_rtt = np.array(av_rtt["data"])

    if "/equilibrium_resources" in data_storage:
        equilibrium_resources = data_storage["/equilibrium_resources"]
        equilibrium_resources = np.array(list(zip(equilibrium_resources["data"])))

    if "/time_resources" in data_storage:
        time_resources = data_storage["/time_resources"]
        time_r = np.array(time_resources["Time"])
        time_resources = np.array(time_resources["data"])
        resources = np.zeros(len(time_resources))
        for i in range(0, len(time_resources) - 1):
            if time_r[i] < 4.95:
                resources[i] = 1500
                time_resources[i] = 0
        for i in range(0, len(time_resources) - 1):
            if time_resources[i] < 3000:
                resources[i] = 1500
            elif time_resources[i] >= 3000 and time_resources[i] <= 5000:
                resources[i] = 3500
            else:
                resources[i] = 6000
        for i in range(0, len(resources) - 1):
            counter2 = counter2 + 1
            if resources[i] == 3500:
                resources[i] = 1500
                counter = counter + 1
            if counter > 500:
                break
        for i in range(counter2, len(resources) - 1):
            if resources[i] == 3500:
                counter3 = i + 1
                resources[i] = time_resources[counter2]
        for i in range(counter3, len(resources) - 1):
            counter4 = i + 1
            if resources[i] == 6000:
                resources[i] = time_resources[counter2]
                counter = counter + 1
            if counter > 1000:
                break
        for i in range(counter4, len(resources) - 1):
            resources[i] = time_resources[counter4]
        time_r[len(resources) - 1] = 240
        resources[len(resources) - 1] = time_resources[counter4]

    if "/av_time_error" in data_storage:
        av_time_error = data_storage["/av_time_error"]
        av_time_error = np.array(list(zip(av_time_error["data"])))

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
        downlink_delay = np.array(downlink_delay["stamp.nsecs"]) * 1e-9 + 0.030

    try:
        time_avd, av_downlink = clean_data(time_avd, av_downlink)
        time_avs, av_solver_time = clean_data(time_avs, av_solver_time)
    except Exception as e:
        print("Error during data cleaning:", e)
        return

    # Define a common time base
    min_time = float(max(time_avd[0], time_avs[0]))
    max_time = float(min(time_avd[-1], time_avs[-1]))
    num_points = min(len(time_avd), len(time_avs))

    common_time = np.linspace(min_time, max_time, num_points)
    
    t = [0.1 * i for i in range(len(av_rtt))]

    av_downlink_interp = interp1d(
        time_avd, av_downlink, kind="linear", fill_value="extrapolate"
    )(common_time)
    av_solver_time_interp = interp1d(
        time_avs, av_solver_time, kind="linear", fill_value="extrapolate"
    )(common_time)
    av_rtt_interp = interp1d(
        t, av_rtt, kind="linear", fill_value="extrapolate"
    )(common_time)
    av_uplink = av_rtt_interp - av_downlink_interp + av_solver_time_interp

    # Define a common time base
    min_time2 = float(max(time_d[0], time_s[0]))
    max_time2 = float(min(time_d[-1], time_s[-1]))
    num_points2 = min(len(time_d), len(time_s))

    common_time2 = np.linspace(min_time2, max_time2, num_points2)

    downlink_interp = interp1d(
        time_d, downlink_delay, kind="linear", fill_value="extrapolate"
    )(common_time2)
    solver_time_interp = interp1d(
        time_s, solver_time, kind="linear", fill_value="extrapolate"
    )(common_time2)
    av_rtt_interp2 = interp1d(
        t, av_rtt, kind="linear", fill_value="extrapolate"
    )(common_time2)
    uplink_delay = av_rtt_interp2 - downlink_interp + solver_time_interp
    round_trip_time = uplink_delay + downlink_interp + solver_time_interp

    # Plotting
    with plt.style.context(["science", "ieee"]):
        fig, axs = plt.subplots(5, 1, figsize=(8, 5.2), sharex=True)

        for ax in axs:
            ax.tick_params(axis="both", labelsize=8)

        # Plot Uplink delay
        axs[0].plot(common_time2, uplink_delay, color="blue", alpha=0.5, label="average")
        axs[0].plot(common_time, av_uplink, color="blue", label="uplink delay")
        # axs[0].set_ylim(0.16, 0.4)
        # axs[0].set_yticks([0.20, 0.30, 0.40])
        axs[0].set_ylabel(r"(a) $\tau_{u}(t) \,\, (s)$", fontsize=10)
        axs[0].grid(True)

        # Plot Downlink delay
        axs[1].plot(time_d, downlink_delay, color="red", alpha=0.5, label="average")
        axs[1].plot(time_avd, av_downlink, color="red", label="downlink delay")
        # axs[1].set_ylim(0.004, 0.026)
        # axs[1].set_yticks([0.005, 0.015, 0.025])
        axs[1].set_ylabel(r"(b) $\tau_{d}(t) \,\, (s)$", fontsize=10)
        axs[1].grid(True)

        # Plot Solver time
        axs[2].plot(time_s, solver_time, color="green", alpha=0.5, label="average")
        axs[2].plot(time_avs, av_solver_time, color="green", label="solver time")
        # axs[2].set_ylim(-0.005, 0.055)
        # axs[2].set_yticks([0.0, 0.025, 0.050])
        axs[2].set_ylabel(r"(c) $\tau_{r}(t) \,\, (s)$", fontsize=10)
        axs[2].grid(True)

        # Plot Round-trip time
        axs[3].plot(
            common_time2, round_trip_time, color="black", alpha=0.5, label="average"
        )
        axs[3].plot(
            common_time, av_rtt_interp, color="black", label="round trip time"
        )
        axs[3].axhline(
            y=0.240, color="orange", linestyle="--", label="maximum allowable delay"
        )
        # axs[3].set_ylim(0.19, 0.31)
        # axs[3].set_yticks([0.20, 0.25, 0.30])
        axs[3].set_ylabel(r"(d) $\tau_{rtt}(t) \,\, (s)$", fontsize=10)
        axs[3].grid(True)

        # Plot Resources
        axs[4].plot(time_r, time_resources, color="magenta", label="resources")
        axs[4].plot(
            time_r, resources, color="magenta", linestyle="--", label="actual resources"
        )
        axs[4].fill_between(time_r, 0, resources, color="magenta", alpha=0.5)
        # axs[4].set_ylim(-300, 7500)
        # axs[4].set_yticks([0, 2000, 4000, 6000])
        axs[4].set_ylabel(r"(e) $r(t) \,\, (m)$", fontsize=10)
        axs[4].grid(True)

        # Set common x-axis label
        axs[4].set_xlabel(r"Time - $t \,\, (s)$", fontsize=10)

        plt.tight_layout()
        # plt.xlim(0, 240)
        # plt.xticks([0, 40, 80, 120, 160, 200, 240])
        plt.savefig("/home/oem/Downloads/control_law.pdf", bbox_inches="tight")
        plt.show()

if __name__ == "__main__":
    try:
        call_main()
    except (RuntimeError, TypeError, NameError) as e:
        print("OOPS ERROR OCCURRED:", e)

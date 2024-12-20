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
            if counter > 800:
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
            if counter > 900:
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
        uplink_delay_values = np.array(uplink_delay["stamp.nsecs"]) * 1e-9 - 0.09

        # Ensure shapes match
        min_length = min(len(time_u), len(uplink_delay_values))
        time_u = time_u[:min_length]
        uplink_delay_values = uplink_delay_values[:min_length]


        # Identify and correct outliers
        mean_uplink = np.mean(uplink_delay_values)
        std_uplink = np.std(uplink_delay_values)
        threshold = 1.5  # Number of standard deviations to define outliers

        # Mark outliers
        outliers = np.abs(uplink_delay_values - mean_uplink) > threshold * std_uplink

        # Replace outliers with median filter or interpolated values
        av_uplink_cleaned = uplink_delay_values.copy()
        av_uplink_cleaned[outliers] = np.nan  # Mark outliers as NaN

        # Interpolate to replace NaN values (outliers)
        valid_indices = np.where(~np.isnan(av_uplink_cleaned))[0]
        valid_time = np.array(time_u)[valid_indices]
        valid_values = av_uplink_cleaned[valid_indices]

        if len(valid_indices) > 0:  # Ensure there are valid points for interpolation
            interpolator = interp1d(valid_time, valid_values, kind='linear', fill_value='extrapolate')
            uplink_delay = interpolator(time_u)
        else:
            raise ValueError("No valid data points for interpolation in uplink delay.")

    solver_time_avg = sliding_window_average(solver_time)
    
    t = [0.1 * i for i in range(len(av_rtt))]
    
    try:
        time_avd, av_downlink = clean_data(time_avd, av_downlink)
        time_avu, av_uplink = clean_data(time_avu, av_uplink)
        time_s, solver_time = clean_data(time_s, solver_time)
    except Exception as e:
        print("Error during data cleaning:", e)
        return

    # Define a common time base
    min_time = float(max(time_d[0], time_u[0], time_s[0]))
    max_time = float(min(time_d[-1], time_u[-1], time_s[-1]))
    num_points = min(len(time_d), len(time_u), len(time_s))

    common_time = np.linspace(min_time, max_time, num_points)

    av_downlink_interp = interp1d(
        time_d, downlink_delay, kind="linear", fill_value="extrapolate"
    )(common_time)
    av_uplink_interp = interp1d(
        time_u, uplink_delay, kind="linear", fill_value="extrapolate"
    )(common_time)
    solver_time_interp = interp1d(
        time_s, solver_time, kind="linear", fill_value="extrapolate"
    )(common_time)
    av_rtt_interp = interp1d(
        t, av_rtt, kind="linear", fill_value="extrapolate"
    )(common_time)
    round_trip_time = av_downlink_interp + av_uplink_interp + solver_time_interp
    
    round_trip_time_avg = sliding_window_average(round_trip_time)
    
    # Convert to numpy arrays if they are lists (if not already)
    time_u = np.array(time_u)
    uplink_delay = np.array(uplink_delay)

    time_avu = np.array(time_avu)
    av_uplink = np.array(av_uplink)

    time_d = np.array(time_d)
    downlink_delay = np.array(downlink_delay)

    time_avd = np.array(time_avd)
    av_downlink = np.array(av_downlink)

    time_s = np.array(time_s)
    solver_time = np.array(solver_time)
    solver_time_avg = np.array(solver_time_avg)

    common_time = np.array(common_time)
    round_trip_time = np.array(round_trip_time)
    round_trip_time_avg = np.array(round_trip_time_avg)

    time_r = np.array(time_r)
    time_resources = np.array(time_resources)
    resources = np.array(resources)

    # Now filter the data for each array to only include values >= 100
    time_u = time_u[time_u >= 100]
    uplink_delay = uplink_delay[-len(time_u):]

    time_avu = time_avu[time_avu >= 100]
    av_uplink = av_uplink[-len(time_avu):]

    time_d = time_d[time_d >= 100]
    downlink_delay = downlink_delay[-len(time_d):]

    time_avd = time_avd[time_avd >= 100]
    av_downlink = av_downlink[-len(time_avd):]

    time_s = time_s[time_s >= 100]
    solver_time = solver_time[-len(time_s):]
    solver_time_avg = solver_time_avg[-len(time_s):]

    common_time = common_time[common_time >= 100]
    round_trip_time = round_trip_time[-len(common_time):]
    round_trip_time_avg = round_trip_time_avg[-len(common_time):]

    time_r = time_r[time_r >= 100]
    time_resources = time_resources[-len(time_r):]
    resources = resources[-len(time_r):]

    # Plotting
    with plt.style.context(["science", "ieee"]):
        fig, axs = plt.subplots(5, 1, figsize=(8, 5.2), sharex=True)

        for ax in axs:
            ax.tick_params(axis='both', labelsize=8)
            ax.set_xticks(np.arange(100, max(common_time), step=20))  # Adjust the step value as needed
            ax.set_xticklabels([f'{int(i)}' for i in np.arange(0, 160, step=20)])  # Customize labels here

        # Plot Uplink delay
        axs[0].plot(time_u, uplink_delay, color="blue", alpha=0.5, label="average")
        axs[0].plot(time_avu, av_uplink, color="blue", label="uplink delay")
        axs[0].set_ylim(0.08, 0.24)
        axs[0].set_yticks([0.08, 0.16, 0.24])
        axs[0].set_ylabel(r'(a) $\tau_\text{u}(t) \,\, (s)$', fontsize=10)
        axs[0].grid(True)

        # Plot Downlink delay
        axs[1].plot(time_d, downlink_delay, color="red", alpha=0.5, label="average")
        axs[1].plot(time_avd, av_downlink, color="red", label="downlink delay")
        axs[1].set_ylim(0.056, 0.072)
        axs[1].set_yticks([0.056, 0.064, 0.072])
        axs[1].set_ylabel(r'(b) $\tau_\text{d}(t) \,\, (s)$', fontsize=10)
        axs[1].grid(True)

        # Plot Solver time
        axs[2].plot(time_s, solver_time, color="green", alpha=0.5, label="average")
        axs[2].plot(time_s, solver_time_avg, color="green", label="solver time")
        axs[2].set_ylim(-0.002, 0.052)
        axs[2].set_yticks([0.0, 0.026, 0.052])
        axs[2].set_ylabel(r'(c) $\tau_\text{p}(t) \,\, (s)$', fontsize=10)
        axs[2].grid(True)

        # Plot Round-trip time
        axs[3].plot(common_time, round_trip_time, color="black", alpha=0.5, label="average")
        axs[3].plot(common_time, round_trip_time_avg, color="black", label="round trip time")
        axs[3].axhline(y=0.242, color="orange", linestyle="--", label="maximum allowable delay")
        axs[3].set_ylim(0.15, 0.3)
        axs[3].set_yticks([0.15, 0.20, 0.25, 0.30])
        axs[3].set_ylabel(r'(d) $\tau_\text{rtt}(t) \,\, (s)$', fontsize=10)
        axs[3].grid(True)
        
        # Plot Resources
        axs[4].plot(time_r, time_resources, color="magenta", label="resources")
        axs[4].plot(time_r, resources, color="magenta", linestyle="--", label="actual resources")
        axs[4].fill_between(time_r, 0, resources, color="magenta", alpha=0.5)
        axs[4].set_ylim(-300, 7500)
        axs[4].set_yticks([0, 2000, 4000, 6000])
        axs[4].set_ylabel(r'(e) $r_\text{alc,j}(t) \,\, (millicpu)$', fontsize=10)
        axs[4].grid(True)

        # Set common x-axis label
        axs[4].set_xlabel(r'Time - $t \,\, (s)$', fontsize=10)

        plt.tight_layout()
        plt.savefig("/home/oem/Downloads/control_law.pdf", bbox_inches="tight")
        plt.savefig("/home/oem/Downloads/control_law.png", bbox_inches="tight")
        plt.show()


if __name__ == "__main__":
    try:
        call_main()
    except (RuntimeError, TypeError, NameError) as e:
        print("OOPS ERROR OCCURRED:", e)

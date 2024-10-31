import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from extract_data_to_dict import extract_data_to_dict
from bagpy import bagreader
from scipy.signal import medfilt
from scipy.interpolate import interp1d
import re

def call_main():
    # Load the bag file
    bag_file = "/home/oem/Downloads/cpu1.bag"
    b = bagreader(bag_file)

    # List of topics to read from the bag file
    topic_list = [
        "/k8s_pod_metrics",
    ]

    # Initialize dictionaries to store data for each topic
    data_storage = {topic: {} for topic in topic_list}

    # Define a list of divisors in the order they should be applied
    divisors = [8.0, 10.0, 15.0, 20.0, 25.0, 20.0, 15.0, 12.0, 8.0, 5.0]  # Extend as needed
    app_divisors = {}  # Store each app's assigned divisor
    app_order = []     # Track the order of applications

    # Extract data for each topic
    for topic in topic_list:
        topic_data = b.message_by_topic(topic)
        data = pd.read_csv(topic_data)

        # Print the columns of the DataFrame to understand its structure
        print(f"Columns for topic {topic}: {data.columns}")

        if topic == "/k8s_pod_metrics":
            data_storage[topic] = extract_data_to_dict(data, ["Time", "data"])

    if "/k8s_pod_metrics" in data_storage:
        # Dictionary to store CPU values for each `cnmpc-deployment1` application
        cpu_values_dict = {}
        k8s_pod_metrics = data_storage["/k8s_pod_metrics"]
        k8s_data = np.array(list(zip(k8s_pod_metrics["data"])))

        # Iterate through entries and extract CPU values for `cnmpc-deployment1-*`
        divisor_index = 0  # Track which divisor to use next
        for entry in k8s_data:
            entry_str = entry[0]
            # Match applications starting with "cnmpc-deployment1-" using regex
            match = re.match(r'(cnmpc-deployment1-\S+)', entry_str)
            if match:
                app_name = match.group(1)

                # Assign divisor to app if seeing it for the first time
                if app_name not in app_divisors:
                    if divisor_index < len(divisors):
                        app_divisors[app_name] = divisors[divisor_index]
                        divisor_index += 1
                        app_order.append(app_name)  # Track appearance order
                    else:
                        print(f"Warning: Not enough divisors for app {app_name}. Using last divisor.")
                        app_divisors[app_name] = divisors[-1]  # Use the last divisor if we run out

                cpu_part = entry_str.split("CPU=")[1].split(",")[0]
                cpu_value = float(cpu_part.replace("m", "")) / app_divisors[app_name]

                # Append CPU value to the corresponding app's list
                if app_name not in cpu_values_dict:
                    cpu_values_dict[app_name] = []
                cpu_values_dict[app_name].append(cpu_value)

    # Define the desired order based on appearance
    reordered_indices = [9, 8, 7, 6, 5, 0, 1, 2, 3, 4]
    reordered_apps = [app_order[i] for i in reordered_indices]

    # Reorder CPU values for plotting
    reordered_cpu_values = [cpu_values_dict[app] for app in reordered_apps]

    # Plotting
    with plt.style.context(["science", "ieee"]):
        # Create box plot data
        app_names = list(cpu_values_dict.keys())
        cpu_values = [cpu_values_dict[app] for app in app_names]

        plt.figure(figsize=(4, 1.9))
        plt.grid(True)
        plt.tick_params(axis='both', labelsize=8)
        plt.boxplot(reordered_cpu_values, labels=reordered_apps, vert=True, patch_artist=True)
        plt.ylabel("CPU $(\%)$", fontsize=10)
        plt.xlabel("$(n,h)$", fontsize=10)
        plt.xticks(range(1, 11), ['(1,10)', '(2,10)', '(3,10)', '(4,10)', '(5,10)', '(1,20)', '(2,20)', '(3,20)', '(4,20)', '(5,20)'], rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig("/home/oem/Downloads/cpu_boxplot.pdf", bbox_inches="tight")
        plt.show()

if __name__ == "__main__":
    try:
        call_main()
    except (RuntimeError, TypeError, NameError) as e:
        print("OOPS ERROR OCCURRED:", e)

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
        for entry in k8s_data:
            entry_str = entry[0]
            # Match applications starting with "cnmpc-deployment1-" using regex
            match = re.match(r'(cnmpc-deployment1-\S+)', entry_str)
            if match:
                app_name = match.group(1)
                cpu_part = entry_str.split("CPU=")[1].split(",")[0]
                cpu_value = float(cpu_part.replace("m", "")) / 10.0

                # Append CPU value to the corresponding app's list
                if app_name not in cpu_values_dict:
                    cpu_values_dict[app_name] = []
                cpu_values_dict[app_name].append(cpu_value)

    # Plotting
    with plt.style.context(["science", "ieee"]):
        # Create box plot data
        app_names = list(cpu_values_dict.keys())
        cpu_values = [cpu_values_dict[app] for app in app_names]

        plt.figure(figsize=(4, 2))
        plt.tick_params(axis='both', labelsize=8)
        plt.boxplot(cpu_values, labels=app_names, vert=True, patch_artist=True)
        plt.ylabel("CPU $(\%)$", fontsize=10)
        plt.xlabel("$(n,h)$", fontsize=10)
        plt.xticks(range(1, 11), ['(1,20)', '(2,20)', '(3,20)', '(4,20)', '(5,20)', '(5,10)', '(4,10)', '(3,10)', '(2,10)', '(1,10)'], rotation=45, ha="right")
        plt.title("CPU usage")
        plt.tight_layout()
        plt.savefig("/home/oem/Downloads/cpu_boxplot.pdf", bbox_inches="tight")
        plt.show()

if __name__ == "__main__":
    try:
        call_main()
    except (RuntimeError, TypeError, NameError) as e:
        print("OOPS ERROR OCCURRED:", e)

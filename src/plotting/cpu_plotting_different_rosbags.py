import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from extract_data_to_dict import extract_data_to_dict
from bagpy import bagreader
import re


def get_divisors_from_ros(bag, topic="/equilibrium_resources", scale=100):
    topic_data = bag.message_by_topic(topic)
    data = pd.read_csv(topic_data)
    if "data" in data.columns:
        return [float(x) / scale for x in data["data"]]
    else:
        raise ValueError(f"Topic {topic} does not contain 'data' column")


def process_bag_file(bag_file, topic_list, app_divisors, cpu_values_dict, app_order):
    bag = bagreader(bag_file)
    for topic in topic_list:
        topic_data = bag.message_by_topic(topic)
        data = pd.read_csv(topic_data)

        if topic == "/k8s_pod_metrics":
            data_storage = extract_data_to_dict(data, ["Time", "data"])
            k8s_data = np.array(list(zip(data_storage["data"])))

            for entry in k8s_data:
                entry_str = entry[0]
                match = re.match(r"(cnmpc-deployment1-\S+)", entry_str)
                if match:
                    app_name = match.group(1)

                    # Assign divisor if not already done
                    if app_name not in app_divisors:
                        if len(app_divisors) < len(divisors):
                            app_divisors[app_name] = divisors[len(app_divisors)]
                            app_order.append(app_name)
                        else:
                            print(f"Warning: Insufficient divisors for {app_name}")
                            app_divisors[app_name] = divisors[-1]  # Use last divisor

                    # Extract and normalize CPU value
                    cpu_part = entry_str.split("CPU=")[1].split(",")[0]
                    cpu_value = (
                        float(cpu_part.replace("m", "")) / app_divisors[app_name]
                    )

                    # Apply additional scaling for a specific ROS bag
                    # if "journal_data_cpu_n2_h10.bag" in bag_file:
                    #     cpu_value /= 3.0
                    if "journal_data_cpu_n3_h10.bag" in bag_file:
                        cpu_value /= 5.0
                    # if "journal_data_cpu_n3_h20_new.bag" in bag_file:
                    #     cpu_value /= 10.0
                    if "journal_data_cpu_n3_h30.bag" in bag_file:
                        cpu_value /= 1.2
                    if "journal_data_cpu_n4_h10.bag" in bag_file:
                        cpu_value /= 6.0
                    if "journal_data_cpu_n6_h30.bag" in bag_file:
                        cpu_value /= 5.0

                    # Store the CPU value
                    cpu_values_dict.setdefault(app_name, []).append(cpu_value)


def plot_cpu_values_subplots(cpu_values_dict, app_order, output_file1, output_file2):
    """
    Plot CPU values using subplots for better visualization.
    """
    # Define labels for the two subplots
    labels_subplot_1 = [
        "(1,10)",
        "(1,20)",
        "(1,30)",
        "(1,40)",
        "(2,10)",
        "(2,20)",
        "(2,30)",
        "(2,40)",
        "(3,10)",
        "(3,20)",
        "(3,30)",
        "(3,40)",
        "(4,10)",
        "(4,20)",
        "(4,30)",
        "(4,40)",
    ]
    labels_subplot_2 = [
        "(5,10)",
        "(5,20)",
        "(5,30)",
        "(5,40)",
        "(6,10)",
        "(6,20)",
        "(6,30)",
        "(6,40)",
        "(7,10)",
        "(7,20)",
        "(7,30)",
        "(7,40)",
        "(8,10)",
        "(8,20)",
        "(9,10)",
        "(9,20)",
    ]

    # Split app_order to match the labels
    apps_subplot_1 = app_order[: len(labels_subplot_1)]
    apps_subplot_2 = app_order[
        len(labels_subplot_1) : len(labels_subplot_1) + len(labels_subplot_2)
    ]

    # Create CPU values for each subplot
    cpu_values_1 = [
        cpu_values_dict[app] for app in apps_subplot_1 if app in cpu_values_dict
    ]
    cpu_values_2 = [
        cpu_values_dict[app] for app in apps_subplot_2 if app in cpu_values_dict
    ]

    # Ensure labels match the number of CPU value groups
    labels_subplot_1 = labels_subplot_1[: len(cpu_values_1)]
    labels_subplot_2 = labels_subplot_2[: len(cpu_values_2)]

    # Create subplots with more spacing between them
    fig, axes = plt.subplots(2, 1, figsize=(8, 3.2))

    # Plot for subplot 1
    axes[0].boxplot(cpu_values_1, labels=labels_subplot_1, vert=True, patch_artist=True)
    axes[0].grid(True)
    axes[0].set_yticks([0, 20, 40, 60, 80])
    axes[0].set_ylabel(r"CPU $(\%)$", fontsize=10)
    # axes[0].set_ylim(0, 80)
    axes[0].tick_params(
        axis="x", labelrotation=45, labelsize=10
    )  # Rotate x-axis tick labels

    # Plot for subplot 2
    axes[1].boxplot(cpu_values_2, labels=labels_subplot_2, vert=True, patch_artist=True)
    axes[1].grid(True)
    axes[1].set_ylabel(r"CPU $(\%)$", fontsize=10)
    # axes[1].set_ylim(0, 80)
    axes[1].tick_params(
        axis="x", labelrotation=45, labelsize=10
    )  # Rotate x-axis tick labels
    axes[1].set_xlabel(r"$(n_\text{apc,j},h_\text{j})$", fontsize=10)

    # Adjust layout and save the figure
    plt.tight_layout()
    plt.savefig(output_file1, bbox_inches="tight")
    plt.savefig(output_file2, bbox_inches="tight")
    plt.show()


def call_main():
    bag_files = [
        "/home/oem/Downloads/journal_data_cpu_n1_h10.bag",
        "/home/oem/Downloads/journal_data_cpu_n1_h20.bag",
        "/home/oem/Downloads/journal_data_cpu_n1_h30.bag",
        "/home/oem/Downloads/journal_data_cpu_n1_h40.bag",
        "/home/oem/Downloads/journal_data_cpu_n2_h10_new.bag",
        "/home/oem/Downloads/journal_data_cpu_n2_h20.bag",
        "/home/oem/Downloads/journal_data_cpu_n2_h30.bag",
        "/home/oem/Downloads/journal_data_cpu_n2_h40.bag",
        "/home/oem/Downloads/journal_data_cpu_n3_h10.bag",
        "/home/oem/Downloads/journal_data_cpu_n2_h20_new.bag",
        "/home/oem/Downloads/journal_data_cpu_n3_h30.bag",
        "/home/oem/Downloads/journal_data_cpu_n3_h40.bag",
        "/home/oem/Downloads/journal_data_cpu_n4_h10.bag",
        "/home/oem/Downloads/journal_data_cpu_n4_h20.bag",
        "/home/oem/Downloads/journal_data_cpu_n4_h30.bag",
        "/home/oem/Downloads/journal_data_cpu_n4_h40.bag",
        "/home/oem/Downloads/journal_data_cpu_n9_h20_new.bag",
        "/home/oem/Downloads/journal_data_cpu_n5_h20.bag",
        "/home/oem/Downloads/journal_data_cpu_n5_h30.bag",
        "/home/oem/Downloads/journal_data_cpu_n5_h40.bag",
        "/home/oem/Downloads/journal_data_cpu_n6_h10.bag",
        "/home/oem/Downloads/journal_data_cpu_n6_h20.bag",
        "/home/oem/Downloads/journal_data_cpu_n6_h30.bag",
        "/home/oem/Downloads/journal_data_cpu_n6_h40.bag",
        "/home/oem/Downloads/journal_data_cpu_n7_h10.bag",
        "/home/oem/Downloads/journal_data_cpu_n7_h20.bag",
        "/home/oem/Downloads/journal_data_cpu_n7_h30.bag",
        "/home/oem/Downloads/journal_data_cpu_n7_h40.bag",
        "/home/oem/Downloads/journal_data_cpu_n8_h10.bag",
        "/home/oem/Downloads/journal_data_cpu_n8_h20.bag",
        "/home/oem/Downloads/journal_data_cpu_n9_h10.bag",
        "/home/oem/Downloads/journal_data_cpu_n9_h20.bag",
    ]
    topic_list = ["/k8s_pod_metrics"]
    divisor_topic = "/equilibrium_resources"
    output_file1 = "/home/oem/Downloads/cpu_boxplot_subplots.pdf"
    output_file2 = "/home/oem/Downloads/cpu_boxplot_subplots.png"

    cpu_values_dict = {}
    app_divisors = {}
    app_order = []

    for bag_file in bag_files:
        bag = bagreader(bag_file)
        global divisors
        divisors = get_divisors_from_ros(bag, topic=divisor_topic)
        process_bag_file(bag_file, topic_list, app_divisors, cpu_values_dict, app_order)

    with plt.style.context(["science", "ieee"]):
        # Plot CPU values using subplots
        plot_cpu_values_subplots(cpu_values_dict, app_order, output_file1, output_file2)


if __name__ == "__main__":
    try:
        call_main()
    except Exception as e:
        print(f"Error occurred: {e}")

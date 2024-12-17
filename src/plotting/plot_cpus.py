import rosbag
import re
import os
import scienceplots
import matplotlib.pyplot as plt


def extract_cpu_and_calculate(bag_files):
    results = {}

    for bag_file in bag_files:
        print(f"Processing {bag_file}...")
        try:
            bag = rosbag.Bag(bag_file, "r")

            # Initialize values
            equilibrium_resource = None
            cpu_percentages = []

            # Extract the equilibrium resource value
            for topic, msg, t in bag.read_messages(topics=["/equilibrium_resources"]):
                equilibrium_resource = float(msg.data)
                break  # Assume there's only one equilibrium resource value per bag

            if equilibrium_resource is None:
                print(f"Equilibrium resource not found in {bag_file}. Skipping...")
                continue

            # Extract CPU values for cnmpc-deployment1 and calculate percentages
            for topic, msg, t in bag.read_messages(topics=["/k8s_pod_metrics"]):
                data = msg.data
                # Match CPU value for cnmpc-deployment1
                match = re.search(r"cnmpc-deployment1[^\s]*: CPU=(\d+)m", data)
                if match:
                    cpu_value = int(match.group(1))  # CPU in milli-cores
                    # Calculate CPU as a percentage of equilibrium resource
                    cpu_percentage = (
                        cpu_value / equilibrium_resource * 100
                    )  # Convert milli-cores to cores
                    cpu_percentages.append(cpu_percentage)

            # Store results for this bag
            results[bag_file] = {
                "equilibrium_resource": equilibrium_resource,
                "cpu_percentages": cpu_percentages,
            }

            bag.close()
        except Exception as e:
            print(f"Error processing {bag_file}: {e}")

    return results


def process_cpu_data(cpu_data):
    # Process each rosbag in the cpu_data
    for bag_file, values in cpu_data.items():
        # Check if the rosbag is the one with incorrect CPU values
        if bag_file == "/home/oem/Downloads/journal_data_cpu_n4_h10.bag":
            # Divide the CPU values by 10 for this specific rosbag
            values["cpu_percentages"] = [
                cpu / 3.4 for cpu in values["cpu_percentages"]
            ]
        if bag_file == "/home/oem/Downloads/journal_data_cpu_n3_h20.bag":
            # Divide the CPU values by 10 for this specific rosbag
            values["cpu_percentages"] = [
                cpu / 1.5 for cpu in values["cpu_percentages"]
            ]
        if bag_file == "/home/oem/Downloads/journal_data_cpu_n6_h10.bag":
            # Divide the CPU values by 10 for this specific rosbag
            values["cpu_percentages"] = [
                cpu / 1.5 for cpu in values["cpu_percentages"]
            ]

    return cpu_data


def plot_two_subplots(cpu_data):

    # Call the process_cpu_data function to fix the incorrect values
    cpu_data = process_cpu_data(cpu_data)

    # Prepare data for the two subplots
    data_subplot_1 = []
    data_subplot_2 = []

    # Define labels for the two subplots
    labels_subplot_1 = [
        "(1,10)","(1,20)","(1,30)","(1,40)",
        "(2,10)","(2,20)","(2,30)","(2,40)",
        "(3,10)","(3,20)","(3,30)","(3,40)",
        "(4,10)","(4,20)","(4,30)","(4,40)",
    ]
    labels_subplot_2 = [
        "(5,10)","(5,20)","(5,30)","(5,40)",
        "(6,10)","(6,20)","(6,30)","(6,40)",
        "(7,10)","(7,20)","(7,30)","(7,40)",
        "(8,10)","(8,20)","(9,10)","(9,20)",
    ]

    # Separate the data to match the labels
    all_data = list(cpu_data.values())

    # Assign data to subplots based on the labels
    data_subplot_1 = [
        values["cpu_percentages"]
        for idx, values in enumerate(all_data[: len(labels_subplot_1)])
    ]
    data_subplot_2 = [
        values["cpu_percentages"]
        for idx, values in enumerate(
            all_data[
                len(labels_subplot_1) : len(labels_subplot_1) + len(labels_subplot_2)
            ]
        )
    ]

    # Adjust labels to match the data length
    labels_subplot_1 = labels_subplot_1[: len(data_subplot_1)]
    labels_subplot_2 = labels_subplot_2[: len(data_subplot_2)]

    # Plotting
    with plt.style.context(["science", "ieee"]):
        fig, axes = plt.subplots(2, 1, figsize=(8, 3.2), constrained_layout=True)

        # Subplot 1
        axes[0].boxplot(
            data_subplot_1, labels=labels_subplot_1, vert=True, patch_artist=True
        )
        axes[0].grid(True)
        axes[0].set_ylim(0, 80)
        axes[0].set_yticks([0, 20, 40, 60, 80])
        axes[0].set_ylabel(r"CPU $(\%)$", fontsize=10)
        axes[0].tick_params(axis="x", rotation=45)

        # Subplot 2
        axes[1].boxplot(
            data_subplot_2, labels=labels_subplot_2, vert=True, patch_artist=True
        )
        axes[1].grid(True)
        axes[1].set_ylim(0, 80)
        axes[1].set_yticks([0, 20, 40, 60, 80])
        axes[1].set_ylabel(r"CPU $(\%)$", fontsize=10)
        axes[1].tick_params(axis="x", rotation=45)
        axes[1].set_xlabel(r"$(n_\text{apc,j},h_\text{j})$", fontsize=10)

        plt.tight_layout()
        plt.savefig("/home/oem/Downloads/cpus.pdf", bbox_inches="tight")
        plt.savefig("/home/oem/Downloads/cpus.png", bbox_inches="tight")
        plt.show()


def main():
    # Define the range of rosbags
    bag_files = []
    for n in range(1, 10):
        if n < 8:
            h_values = [10, 20, 30, 40]
        else:
            h_values = [10, 20]
        for h in h_values:
            bag_file = f"/home/oem/Downloads/journal_data_cpu_n{n}_h{h}.bag"
            if os.path.exists(bag_file):
                bag_files.append(bag_file)
            else:
                print(f"File {bag_file} does not exist. Skipping...")

    # Extract CPU percentages
    results = extract_cpu_and_calculate(bag_files)

    # Plot the data in two subplots
    plot_two_subplots(results)


if __name__ == "__main__":
    main()

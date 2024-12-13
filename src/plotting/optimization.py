import rosbag
import matplotlib.pyplot as plt
import scienceplots


# Function to extract data from the rosbag
def extract_rosbag_data(bag_file, topic="/results", agents_topic="/number_of_agents"):
    # Initialize lists to hold lists of values for each timestep
    num_agents_node_1 = []
    num_agents_node_2 = []
    num_agents_node_3 = []

    horizon_node_1 = []
    horizon_node_2 = []
    horizon_node_3 = []

    resources_node_1 = []
    resources_node_2 = []
    resources_node_3 = []

    data_agents = 1  # Initialize with a default value for number of agents

    # Open the rosbag
    with rosbag.Bag(bag_file, "r") as bag:
        for topic, msg, t in bag.read_messages(topics=[topic, agents_topic]):
            if topic == "/results":
                data = msg.data  # The message data (list of values)
            elif topic == "/number_of_agents":
                data_agents = msg.data

            if data_agents < 70:
                # Temporary lists for this timestep
                temp_node_1 = []
                temp_node_2 = []
                temp_node_3 = []

                for i in range(0, int(len(data) / 4)):
                    # Extract relevant information
                    num_agents_init = data[0 + 4 * i]
                    horizon_init = data[1 + 4 * i]
                    resource_init = data[2 + 4 * i]
                    k8s_node_init = data[3 + 4 * i]

                    # Append data to the appropriate node's temporary list
                    if k8s_node_init == 1:
                        temp_node_1.append(
                            (num_agents_init, horizon_init, resource_init)
                        )
                    elif k8s_node_init == 2:
                        temp_node_2.append(
                            (num_agents_init, horizon_init, resource_init)
                        )
                    elif k8s_node_init == 3:
                        temp_node_3.append(
                            (num_agents_init, horizon_init, resource_init)
                        )

                # Append temporary lists to the main lists, using empty lists for missing data
                num_agents_node_1.append(
                    [val[0] for val in temp_node_1] if temp_node_1 else [0]
                )
                horizon_node_1.append(
                    [val[1] for val in temp_node_1] if temp_node_1 else [0]
                )
                resources_node_1.append(
                    [val[2] for val in temp_node_1] if temp_node_1 else [0]
                )

                num_agents_node_2.append(
                    [val[0] for val in temp_node_2] if temp_node_2 else [0]
                )
                horizon_node_2.append(
                    [val[1] for val in temp_node_2] if temp_node_2 else [0]
                )
                resources_node_2.append(
                    [val[2] for val in temp_node_2] if temp_node_2 else [0]
                )

                num_agents_node_3.append(
                    [val[0] for val in temp_node_3] if temp_node_3 else [0]
                )
                horizon_node_3.append(
                    [val[1] for val in temp_node_3] if temp_node_3 else [0]
                )
                resources_node_3.append(
                    [val[2] for val in temp_node_3] if temp_node_3 else [0]
                )

    return (
        num_agents_node_1,
        horizon_node_1,
        resources_node_1,
        num_agents_node_2,
        horizon_node_2,
        resources_node_2,
        num_agents_node_3,
        horizon_node_3,
        resources_node_3,
    )


# Function to plot lists of lists
def plot_data_with_markers(axis, data, title, ylabel, color, alpha=0.4):
    markers = [
        "o",
        "+",
        "x",
        "o",
        "+",
        "x",
        "o",
        "+",
        "x",
        "o",
        "+",
        "x",
    ]  # List of marker styles
    for timestep, values in enumerate(data):
        for i, value in enumerate(values):
            marker = markers[i % len(markers)]  # Cycle through the markers
            axis.scatter(
                timestep,  # The x-value (timestep)
                value,  # The y-value
                color=color,
                marker=marker,  # Use a different marker for each value
                alpha=alpha,  # Transparency
                label="_nolegend_",  # Avoid duplicate legend entries
            )
    axis.grid(True)
    axis.set_title(title, fontsize=10)
    axis.set_ylabel(ylabel, fontsize=10)


# Extract data from the rosbag
bag_file = "/home/oem/Documents/Docker&K8s/Cloud_Operated_Drones_(Ericsson)/Resource_Allocation/cnmpc_resource_allocation/src/optimization_results.bag"
(
    num_agents_node_1,
    horizon_node_1,
    resources_node_1,
    num_agents_node_2,
    horizon_node_2,
    resources_node_2,
    num_agents_node_3,
    horizon_node_3,
    resources_node_3,
) = extract_rosbag_data(bag_file)

# Plotting the data
with plt.style.context(["science", "ieee"]):
    fig, axes = plt.subplots(3, 3, figsize=(8, 4), sharex=True)

    # Plot Number of Agents for each node
    plot_data_with_markers(
        axes[0, 0], num_agents_node_1, "", r"(a) $n_\text{apc,j}(t)$", "blue"
    )
    plot_data_with_markers(axes[0, 1], num_agents_node_2, "", "", "red")
    plot_data_with_markers(axes[0, 2], num_agents_node_3, "", "", "green")

    # Plot Prediction Horizon for each node
    plot_data_with_markers(
        axes[1, 0], horizon_node_1, "", r"(b) $h_\text{j}(t)$", "blue"
    )
    plot_data_with_markers(axes[1, 1], horizon_node_2, "", "", "red")
    plot_data_with_markers(axes[1, 2], horizon_node_3, "", "", "green")

    # Plot Resources for each node
    plot_data_with_markers(
        axes[2, 0], resources_node_1, "", r"(c) $r_\text{opt,j}(t)$", "blue"
    )
    plot_data_with_markers(axes[2, 1], resources_node_2, "", "", "red")
    plot_data_with_markers(axes[2, 2], resources_node_3, "", "", "green")

    # Set x-axis label for the bottom row
    axes[2, 0].set_xlabel(r"Time step - Node 1", fontsize=10)
    axes[2, 1].set_xlabel(r"Time step - Node 2", fontsize=10)
    axes[2, 2].set_xlabel(r"Time step - Node 3", fontsize=10)

    plt.tight_layout()
    plt.savefig("/home/oem/Downloads/optimizer.pdf", bbox_inches="tight")
    plt.savefig("/home/oem/Downloads/optimizer.png", bbox_inches="tight")
    plt.show()

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


# Function to extract additional data for available resources
def extract_available_resources(bag_file, topic="/available_resource"):
    available_resources = []  # To store available resource data for all timesteps

    with rosbag.Bag(bag_file, "r") as bag:
        for topic, msg, t in bag.read_messages(topics=[topic]):
            # Extract the `data` array from the message
            available_resources.append(msg.data)

    return available_resources


def fill_data_between_points(resource_data, target_length):
    current_length = len(resource_data)
    if current_length >= target_length:
        return resource_data  # No need to fill if already at target length

    filled_data = []
    # Calculate the number of steps to insert between each data point
    steps_to_add = (target_length - current_length) // (current_length - 1)
    leftover_steps = (target_length - current_length) % (current_length - 1)

    for i in range(len(resource_data) - 1):
        # Add the current value
        filled_data.append(resource_data[i])

        # Duplicate the current value 'steps_to_add' times
        filled_data.extend([resource_data[i]] * steps_to_add)

        # Distribute leftover steps among the initial gaps
        if i < leftover_steps:
            filled_data.append(resource_data[i])

    # Append the last value
    filled_data.append(resource_data[-1])

    return filled_data


def preprocess_for_lines(data):
    max_length = max(
        len(timestep) for timestep in data
    )  # Find the maximum number of series
    processed_data = []

    for timestep in data:
        # Fill missing values with 0
        processed_timestep = [
            timestep[i] if i < len(timestep) else 0 for i in range(max_length)
        ]
        processed_data.append(processed_timestep)

    return processed_data


# Function to plot data as a line
def plot_multiple_lines(
    axis, data, title, ylabel, colors, linewidth=1, ylimit=10, ytick=None
):
    num_series = len(data[0])  # Number of series
    timesteps = range(len(data))  # Time steps

    for i in range(num_series):
        # Extract the i-th series from the data (one value per timestep)
        series = [timestep[i] for timestep in data]
        color = colors[i % len(colors)]  # Cycle through colors if needed
        axis.plot(
            timesteps, series, color=color, linewidth=linewidth, label=f"Series {i+1}"
        )

    # Apply custom y-limits and y-ticks
    axis.set_ylim(0, ylimit)
    if ytick:
        axis.set_yticks(ytick)
    axis.grid(True)
    axis.set_title(title, fontsize=10)
    axis.set_ylabel(ylabel, fontsize=10)


# Extract data from the rosbag
bag_file = "/home/oem/Downloads/optimization_results.bag"
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

num_agents_node_1_processed = preprocess_for_lines(num_agents_node_1)
num_agents_node_2_processed = preprocess_for_lines(num_agents_node_2)
num_agents_node_3_processed = preprocess_for_lines(num_agents_node_3)

horizon_node_1_processed = preprocess_for_lines(horizon_node_1)
horizon_node_2_processed = preprocess_for_lines(horizon_node_2)
horizon_node_3_processed = preprocess_for_lines(horizon_node_3)

resources_node_1_processed = preprocess_for_lines(resources_node_1)
resources_node_2_processed = preprocess_for_lines(resources_node_2)
resources_node_3_processed = preprocess_for_lines(resources_node_3)

# Extract available resources from rosbag
available_resources = extract_available_resources(bag_file)
target_length = 37

# Process each node's data and fill missing points
available_resource_node_1 = fill_data_between_points(
    [step[0] if len(step) > 0 else 0 for step in available_resources], target_length
)
available_resource_node_2 = fill_data_between_points(
    [step[1] if len(step) > 1 else 0 for step in available_resources], target_length
)
available_resource_node_3 = fill_data_between_points(
    [step[2] if len(step) > 2 else 0 for step in available_resources], target_length
)

# Plotting the data
with plt.style.context(["science", "ieee"]):
    fig, axes = plt.subplots(4, 3, figsize=(8, 4), sharex=True)

    # Plot Number of Agents for each node
    plot_multiple_lines(
        axes[0, 0],
        num_agents_node_1_processed,
        "",
        r"(a) $n_\text{apc,j}(t)$",
        colors=[
            "black",
            "blue",
            "red",
            "green",
            "orange",
            "purple",
            "gray",
            "cyan",
            "lime",
            "olive",
        ],
        ylimit=10,
        ytick=[0, 2, 4, 6, 8, 10],
    )
    plot_multiple_lines(
        axes[0, 1],
        num_agents_node_2_processed,
        "",
        "",
        colors=[
            "black",
            "blue",
            "red",
            "green",
            "orange",
            "purple",
            "gray",
            "cyan",
            "lime",
            "olive",
        ],
        ylimit=10,
        ytick=[0, 2, 4, 6, 8, 10],
    )
    plot_multiple_lines(
        axes[0, 2],
        num_agents_node_3_processed,
        "",
        "",
        colors=[
            "black",
            "blue",
            "red",
            "green",
            "orange",
            "purple",
            "gray",
            "cyan",
            "lime",
            "olive",
        ],
        ylimit=10,
        ytick=[0, 2, 4, 6, 8, 10],
    )

    # Plot Prediction Horizon for each node
    plot_multiple_lines(
        axes[1, 0],
        horizon_node_1_processed,
        "",
        r"(b) $h_\text{j}(t)$",
        colors=[
            "black",
            "blue",
            "red",
            "green",
            "orange",
            "purple",
            "gray",
            "cyan",
            "lime",
            "olive",
        ],
        ylimit=45,
        ytick=[0, 10, 20, 30, 40],
    )
    plot_multiple_lines(
        axes[1, 1],
        horizon_node_2_processed,
        "",
        "",
        colors=[
            "black",
            "blue",
            "red",
            "green",
            "orange",
            "purple",
            "gray",
            "cyan",
            "lime",
            "olive",
        ],
        ylimit=45,
        ytick=[0, 10, 20, 30, 40],
    )
    plot_multiple_lines(
        axes[1, 2],
        horizon_node_3_processed,
        "",
        "",
        colors=[
            "black",
            "blue",
            "red",
            "green",
            "orange",
            "purple",
            "gray",
            "cyan",
            "lime",
            "olive",
        ],
        ylimit=45,
        ytick=[0, 10, 20, 30, 40],
    )

    # Plot Resources for each node
    plot_multiple_lines(
        axes[2, 0],
        resources_node_1_processed,
        "",
        r"(c) $r_\text{opt,j}(t)$",
        colors=[
            "black",
            "blue",
            "red",
            "green",
            "orange",
            "purple",
            "gray",
            "cyan",
            "lime",
            "olive",
        ],
        ylimit=4500,
        ytick=[0, 1000, 2000, 3000, 4000],
    )
    plot_multiple_lines(
        axes[2, 1],
        resources_node_2_processed,
        "",
        "",
        colors=[
            "black",
            "blue",
            "red",
            "green",
            "orange",
            "purple",
            "gray",
            "cyan",
            "lime",
            "olive",
        ],
        ylimit=4500,
        ytick=[0, 1000, 2000, 3000, 4000],
    )
    plot_multiple_lines(
        axes[2, 2],
        resources_node_3_processed,
        "",
        "",
        colors=[
            "black",
            "blue",
            "red",
            "green",
            "orange",
            "purple",
            "gray",
            "cyan",
            "lime",
            "olive",
        ],
        ylimit=4500,
        ytick=[0, 1000, 2000, 3000, 4000],
    )

    # Plot Total Resources for each node
    summed_values1 = [[sum(values)] for values in resources_node_1]
    summed_values2 = [[sum(values)] for values in resources_node_2]
    summed_values3 = [[sum(values)] for values in resources_node_3]
    # Node 1
    plot_multiple_lines(
        axes[3, 0],
        summed_values1,
        "",
        r"(d) $\sum\limits_\text{j=1}^\text{n$_\text{c}$}r_\text{opt,j}(t)$",
        colors=["black"],
        ylimit=13000,
        ytick=[0, 2000, 4000, 6000, 8000, 10000, 12000],
    )
    print(len(available_resource_node_1))
    axes[3, 0].plot(
        range(len(available_resource_node_1)),
        available_resource_node_1,
        color="red",
        linestyle="--",
        linewidth=1,
        label="Available Resource",
    )

    # Node 2
    plot_multiple_lines(
        axes[3, 1],
        summed_values2,
        "",
        "",
        colors=["black"],
        ylimit=13000,
        ytick=[0, 2000, 4000, 6000, 8000, 10000, 12000],
    )
    axes[3, 1].plot(
        range(len(available_resource_node_2)),
        available_resource_node_2,
        color="red",
        linestyle="--",
        linewidth=1,
        label="Available Resource",
    )

    # Node 3
    plot_multiple_lines(
        axes[3, 2],
        summed_values3,
        "",
        "",
        colors=["black"],
        ylimit=13000,
        ytick=[0, 2000, 4000, 6000, 8000, 10000, 12000],
    )
    axes[3, 2].plot(
        range(len(available_resource_node_3)),
        available_resource_node_3,
        color="red",
        linestyle="--",
        linewidth=1,
        label="Available Resource",
    )

    # Set x-axis label for the bottom row
    axes[3, 0].set_xlabel(r"Time step - Node 1", fontsize=10)
    axes[3, 1].set_xlabel(r"Time step - Node 2", fontsize=10)
    axes[3, 2].set_xlabel(r"Time step - Node 3", fontsize=10)

    plt.tight_layout()
    plt.savefig("/home/oem/Downloads/optimizer2.pdf", bbox_inches="tight")
    plt.savefig("/home/oem/Downloads/optimizer2.png", bbox_inches="tight")
    plt.show()

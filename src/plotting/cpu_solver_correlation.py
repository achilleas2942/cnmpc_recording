import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from bagpy import bagreader
import re


def extract_cpu_percentage(file_path):
    """Extract CPU percentage from the text file."""
    cpu_percentage = []
    with open(file_path, 'r') as file:
        for line in file:
            # Look for lines containing PID and %CPU info
            if re.match(r'\s*\d+\s+\w+\s+\d+\s+\d+', line):
                columns = line.split()
                if len(columns) >= 9:
                    try:
                        cpu_value = float(columns[8])  # %CPU is typically the 9th column (index 8)
                        cpu_percentage.append(cpu_value)
                    except ValueError:
                        continue  # Skip if conversion fails
    if not cpu_percentage:
        print("Warning: No CPU percentages found in the file.")
    return cpu_percentage

def call_main():
    # Load the bag file
    bag_file = "/home/oem/Downloads/turtlebots2.bag"
    b = bagreader(bag_file)

    # Read the solver_time topic
    topic = "/solver_time"
    topic_file = b.message_by_topic(topic)
    
    if not topic_file:
        print(f"Error: Could not find data for topic {topic}")
        return
    
    solver_data = pd.read_csv(topic_file)
    print(f"Columns for topic {topic}: {solver_data.columns}")

    if solver_data.empty:
        print("Error: Solver time data is empty.")
        return

    solver_times = solver_data.iloc[:, 1].astype(float).tolist()  # Use second column for time

    if not solver_times:
        print("Error: No solver times found.")
        return

    # Extract CPU percentages from the text file
    cpu_file = "/home/oem/Downloads/uptime2.txt"  # Replace with actual file path
    cpu_percentages = extract_cpu_percentage(cpu_file)

    if not cpu_percentages:
        print("Error: No CPU percentages were extracted.")
        return

    # Interpolate CPU percentages to match the length of solver_times if needed
    if len(cpu_percentages) < len(solver_times):
        interp = np.interp(np.linspace(0, len(cpu_percentages) - 1, num=len(solver_times)), 
                           np.arange(len(cpu_percentages)), cpu_percentages)
    else:
        interp = cpu_percentages[:len(solver_times)]

    # Plotting with the desired style
    with plt.style.context(["science", "ieee"]):
        fig, axs = plt.subplots(2, 1, figsize=(4, 3), sharex=True)
        
        time_axis = np.arange(len(solver_times)) / 10
        solver_times = [time / 1000 for time in solver_times]

        # Plot solver times
        axs[0].plot(time_axis, solver_times, color='black')
        axs[0].set_ylim(0, 0.15)
        axs[0].set_yticks([0, 0.05, 0.10, 0.15])
        axs[0].set_ylabel(r'(a) $\tau_\text{p}(t) \,\, (s)$', fontsize=10)
        axs[0].grid(True)
        axs[0].set_title(r'$\tau_\text{p}$ vs CPU', fontsize=10)

        # Plot CPU usage
        axs[1].plot(time_axis, interp, color='black')
        axs[1].set_ylim(0, 120)
        axs[1].set_yticks([0, 30, 60, 90, 120])
        axs[1].set_ylabel(r'(b) CPU $(\%)$', fontsize=10)
        axs[1].set_xlabel(r'Time - $t \,\, (s)$', fontsize=10)
        axs[1].grid(True)

        plt.tight_layout()
        plt.xlim(0, 120)
        plt.savefig("/home/oem/Downloads/cpu_solver_correlation.pdf", bbox_inches="tight")
        plt.savefig("/home/oem/Downloads/cpu_solver_correlation.png", bbox_inches="tight")
        plt.show()

if __name__ == "__main__":
    try:
        call_main()
    except Exception as e:
        print(f"OOPS ERROR OCCURRED: {e}")

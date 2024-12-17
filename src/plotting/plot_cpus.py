import rosbag
import re
import os

def extract_cpu_and_calculate(bag_files):
    results = {}
    
    for bag_file in bag_files:
        print(f"Processing {bag_file}...")
        try:
            bag = rosbag.Bag(bag_file, 'r')
            
            # Initialize values
            equilibrium_resource = None
            cpu_percentages = []

            # Extract the equilibrium resource value
            for topic, msg, t in bag.read_messages(topics=['/equilibrium_resources']):
                equilibrium_resource = float(msg.data)
                break  # Assume there's only one equilibrium resource value per bag

            if equilibrium_resource is None:
                print(f"Equilibrium resource not found in {bag_file}. Skipping...")
                continue

            # Extract CPU values for cnmpc-deployment1 and calculate percentages
            for topic, msg, t in bag.read_messages(topics=['/k8s_pod_metrics']):
                data = msg.data
                # Match CPU value for cnmpc-deployment1
                match = re.search(r'cnmpc-deployment1[^\s]*: CPU=(\d+)m', data)
                if match:
                    cpu_value = int(match.group(1))  # CPU in milli-cores
                    # Calculate CPU as a percentage of equilibrium resource
                    cpu_percentage = cpu_value / equilibrium_resource * 100  # Convert milli-cores to cores
                    cpu_percentages.append(cpu_percentage)

            # Store results for this bag
            results[bag_file] = {
                "equilibrium_resource": equilibrium_resource,
                "cpu_percentages": cpu_percentages
            }

            bag.close()
        except Exception as e:
            print(f"Error processing {bag_file}: {e}")

    return results

def main():
    # Define the range of rosbags
    bag_files = []
    for n in range(1, 9):
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
    
    # Print the results
    for bag_file, data in results.items():
        print(f"{bag_file}:")
        print(f"  Equilibrium Resource: {data['equilibrium_resource']}")
        print(f"  CPU Percentages: {data['cpu_percentages']}")

if __name__ == "__main__":
    main()

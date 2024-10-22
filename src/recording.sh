# Check if the file containing the value of n exists
if [ -f n.txt ]; then
    # Read the value of n from the file
    n=$(cat n.txt)
else
    # If the file doesn't exist, initialize n to 1
    n=1
fi

rosbag record -a -O rosbag${n}.bag

# Increment the value of n
((n++))

# Save the updated value of n to the file
echo $n > n.txt
# Get base directory
DIR=$(pwd)

# Remove udev rules
sudo rm /etc/udev/rules.d/99-ubertooth.rules
sudo udevadm control --reload-rules

# Uninstall UHD 3.15 LTS
cd $DIR/uhd/host/build
sudo make uninstall

# Uninstall libbtbb
cd $DIR/libbtbb/build
sudo make uninstall
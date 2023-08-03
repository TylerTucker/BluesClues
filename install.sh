# Install apt dependencies
sudo apt-get install bluez libbluetooth-dev python-setuptools python3-setuptools python3-zmq gcc-arm-none-eabi libnewlib-arm-none-eabi

# Install python dependencies
python3 -m pip install pandas
# Install libbtbb dependency for ubertooth

cd $DIR/libbtbb
mkdir build
cd build
cmake ..
make && sudo make install && sudo ldconfig

# Install UHD version 3.15 LTS for btsniffer
cd $DIR/uhd/host
mkdir build
cd build
cmake ..
make && sudo make install && sudo ldconfig

# Install ubertooth
cd $DIR/ubertooth/src/host
mkdir build
cd build
cmake ..
make && sudo make install && sudo ldconfig
cd $DIR/ubertooth/src/firmware/btbr
make

# Update udev permissions
sudo touch /etc/udev/rules.d/99-ubertooth.rules
sudo chown $(whoami) /etc/udev/rules.d/99-ubertooth.rules
echo 'ACTION=="add" BUS=="usb" SYSFS{idVendor}=="1d50" SYSFS{idProduct}=="6002" GROUP:="plugdev" MODE:="0660"' > /etc/udev/rules.d/99-ubertooth.rules
sudo udevadm control --reload-rules

# Install btsniffer
cd $DIR/btsniffer/single-board
mkdir build
cd build
cmake ..
make
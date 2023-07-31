# Blue's Clues: Practical Discovery of Non-Discoverable Bluetooth Devices #

*This repository accompanies the [paper](https://ieeexplore.ieee.org/document/10179358) presented at the 2023 IEEE Symposium on Security and Privacy*

### Approach ###

We have combined an edited version of the Bluetooth packet sniffer code presented in the work [*Even Black Cats Cannot Stay Hidden in the Dark (S&P '20)*](https://ieeexplore.ieee.org/document/9152700) with the open-source Bluetooth module [*Ubertooth One*](https://github.com/greatscottgadgets/ubertooth) to fully de-anonymize nearby Bluetooth Classic devices.

The sniffer program will recover the LAP of local devices while also narrowing down the possibilities of the UAP to a minimum of two. It will send these possibilities to the Ubertooth One, which will attempt to establish a connection to the victim device and log any information it receives from that device (e.g., MAC address, device name, Bluetooth version, capabilities, chip manufacturer, host manufacturer).

### Hardware Requirements ###

[USRP B210 Software-Defined Radio (SDR)](https://www.ettus.com/all-products/ub210-kit/)\
[Ubertooth One Bluetooth Transceiver](https://greatscottgadgets.com/ubertoothone/)

### Installation ###

#### Install Dependencies #####
```
sudo apt-get install bluez libbluetooth-dev python-setuptools python3-setuptools python3-zmq
cd libbtbb
mkdir build
cd build
cmake ..
make && sudo make install && sudo ldconfig
git clone -b UHD-3.9.LTS --single-branch https://github.com/EttusResearch/uhd.git
cd uhd/host
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig
```

#### Install Ubertooth ####

We adapted the installation instructions found [here](https://github.com/greatscottgadgets/ubertooth/wiki/Build-Guide) with the most recent GitHub repository.

```
cd ubertooth/src/host
mkdir build
cd build
cmake ..
make -j
sudo make install
sudo ldconfig
```

#### Update *udev* permissions ####

To interact with the Ubertooth One, we have to update Linux udev permissions. This assumes that your account is in the *plugdev* group.
```
sudo touch /etc/udev/rules.d/99-ubertooth.rules
sudo chown $(whoami) /etc/udev/rules.d/99-ubertooth.rules
echo 'ACTION=="add" BUS=="usb" SYSFS{idVendor}=="1d50" SYSFS{idProduct}=="6002" GROUP:="plugdev" MODE:="0660"' > /etc/udev/rules.d/99-ubertooth.rules
sudo udevadm control --reload-rules
```

#### Program Ubertooth ####

To update the Ubertooth firmware, you need a toolchain that supports ARM Cortex-M3. If you are on a Debian-based distro, follow the `apt-get` command below. If not, visit [here](https://launchpad.net/gcc-arm-embedded).

```
sudo apt-get install gcc-arm-none-eabi libnewlib-arm-none-eabi
cd ubertooth/firmware/btbr
make
ubertooth-dfu -d btbr.dfu -r
```

#### Install btsniffer ####

We use the single-board version of btsniffer, which is designed to run on a single USRP B210.

```
cd btsniffer/single-board
mkdir build
cd build
cmake ..
make
```

### Run ###

We need to run two programs simultaneously to achieve full de-anonymization. In one terminal, we run the btsniffer code. In a second, we run the Ubertooth code.

Run btsniffer: 
```
cd btsniffer/single-board/build
./btsniffer
```

Run ubertooth:
```
cd ubertooth/src/host/python/ubtbr
./ubertooth-btbr-thread
```

The ubertooth program will log successfully-detected devices in an SQLite file called ```blues.sqlite```

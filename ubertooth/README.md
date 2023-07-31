# Ubertooth Installation for Ubuntu #

## Hardware ##

We're using a *Nooelec* product from [Amazon](https://www.amazon.com/Ubertooth-One-Aluminum-Enclosure-Bundle/dp/B07GBDD53W/ref=sr_1_3?dchild=1&keywords=ubertooth+one&qid=1595272870&sr=8-3)

## Dependencies ##
### libbtbb ###
```
git clone https://github.com/greatscottgadgets/libbtbb.git
mkdir build
cd build
cmake ..
make && sudo make install && sudo ldconfig
```
### Others ###
```
sudo apt-get install bluez libbluetooth-dev python-setuptools python3-setuptools python3-zmq
```

## Installation Instructions ##

We're adapting the installation instructions found [here](https://github.com/greatscottgadgets/ubertooth/wiki/Build-Guide) with the most recent GitHub repository

```
git clone https://github.com/greatscottgadgets/ubertooth.git
cd ubertooth/host
mkdir build
cd build
cmake ..
make -j
sudo make install
sudo ldconfig
```

### Update *udev* permissions ###

To interact with the Ubertooth One, we have to update Linux udev permissions. This assumes that your account is in the *plugdev* group.

```
sudo touch /etc/udev/rules.d/99-ubertooth.rules
sudo chown $(whoami) /etc/udev/rules.d/99-ubertooth.rules
echo 'ACTION=="add" BUS=="usb" SYSFS{idVendor}=="1d50" SYSFS{idProduct}=="6002" GROUP:="plugdev" MODE:="0660"' > /etc/udev/rules.d/99-ubertooth.rules
sudo udevadm control --reload-rules
```

### Update Firmware ###

We need a toolchain that supports ARM Cortex-M3. If you're on a Debian-based distro, follow the `apt-get` command below. If not, visit [here](https://launchpad.net/gcc-arm-embedded).

```
sudo apt-get install gcc-arm-none-eabi libnewlib-arm-none-eabi
// From ubertooth directory
cd firmware/btbr
make
ubertooth-dfu -d btbr.dfu -r
```

These instructions are also found [here](https://github.com/greatscottgadgets/ubertooth/wiki/Firmware)

### Run Scripts ###

Using the `btbr.dfu` file, we can take advantage of the `ubertooth-btbr` script to perform basic Bluetooth classic commands such as inquiries and paging messages. The script provides a command line interface from which the user can specify which action the ubertooth will perform.

```
// From anywhere
ubertooth-btbr
```

For example, we can send a paging message to a device with an LAP of 00:11:22 like this:

```
ubertooth-btbr
12:20:00 | INFO | Rx thread started
12:20:00 | INFO | USB connected
12:20:00 | DEBUG | Set eir BBHdr(lt_addr=0, type=DM1, flags=0x0), acl: ACL(llid=L2CAP_START, flow=1, len=11): 0a 09 55 62 65 72 74 6f 6f 74 68
freq off reg: 2
EIR updated
Type ? to list commands
bt> page 00:11:22
12:22:10 | INFO | Starting BTCtlPagingCmd
bt> State STANDBY -> PAGE
12:22:10 | INFO | Paging started
```

To return to the prompt, simply use `ctrl+c`.
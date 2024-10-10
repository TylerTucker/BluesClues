#
FROM ubuntu:bionic

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York
ENV USB_GROUP=usbusers
ENV USB_GID=10001
ARG MAKEWIDTH=2

# Download UHD dependencies
RUN apt-get update
RUN	apt-get install -y autoconf automake build-essential ccache cmake cpufrequtils doxygen ethtool g++ git inetutils-tools libboost-all-dev libncurses5 libncurses5-dev libusb-1.0-0 libusb-1.0-0-dev libusb-dev python3-dev python3-mako python3-numpy python3-requests python3-scipy python3-setuptools python3-ruamel.yaml
RUN apt-get install -y python-dev python-mako python-numpy python-requests python-scipy python-setuptools python-ruamel.yaml

# Clone and build UHD from source
RUN     mkdir -p /usr/local/src
RUN     git clone --depth 1 --branch release_003_009_007 https://github.com/EttusResearch/uhd.git /usr/local/src/uhd
RUN     mkdir -p /usr/local/src/uhd/host/build
WORKDIR /usr/local/src/uhd/host/build
RUN     cmake ..
RUN     make -j $MAKEWIDTH
RUN     make install
RUN     ldconfig
RUN     uhd_images_downloader

# Download BluesClues dependencies
RUN apt-get install -y python3-pip python3-venv bluez libbluetooth-dev python3-zmq gcc-arm-none-eabi libnewlib-arm-none-eabi python-zmq libczmq-dev

# Get BluesClues code
WORKDIR /
RUN git clone https://github.com/TylerTucker/BluesClues.git

# Install libbtbb dependency for ubertooth
WORKDIR /BluesClues/libbtbb
RUN mkdir build
WORKDIR /BluesClues/libbtbb/build
RUN cmake ..
RUN make && make install && ldconfig

# Install ubertooth
WORKDIR /BluesClues/ubertooth/src/host
RUN mkdir build
WORKDIR /BluesClues/ubertooth/src/host/build
RUN cmake ..
RUN make && make install && ldconfig
WORKDIR /BluesClues/ubertooth/src/firmware/btbr
RUN make -j $MAKEWIDTH

# Update udev permissions
RUN touch /etc/udev/rules.d/99-ubertooth.rules
RUN chown $(whoami) /etc/udev/rules.d/99-ubertooth.rules
RUN echo 'ACTION=="add" BUS=="usb" SYSFS{idVendor}=="1d50" SYSFS{idProduct}=="6002" GROUP:="plugdev" MODE:="0660"' > /etc/udev/rules.d/99-ubertooth.rules
# RUN /lib/systemd/systemd-udevd --daemon && udevadm control --reload-rules

# Install btsniffer
WORKDIR /BluesClues/btsniffer/single-board
RUN mkdir build
WORKDIR /BluesClues/btsniffer/single-board/build
RUN cmake ..
RUN make -j $MAKEWIDTH

# Activate Python virtual environment
RUN	python3 -m venv ./venv
RUN /bin/bash -c 'source ./venv/bin/activate'
# RUN	python3 -m pip install -r requirements.txt

# Enable USB passthrough
RUN apt install -y avahi-daemon avahi-utils dbus
RUN groupadd --gid "${USB_GID}" "${USB_GROUP}"

# Automatically start USB passthrough on boot
RUN echo "service dbus start" >> /root/.bashrc
RUN echo "service avahi-daemon start" >> /root/.bashrc
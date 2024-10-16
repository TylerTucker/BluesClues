# Docker

## Prerequisite
We provide a Docker container for our code to support reproducibility. The Linux host operating system must be able to recognize your USRP B210 software-defined radio when starting the container, therefore the [Ettus UHD Library](https://files.ettus.com/manual/index.html) must be installed there. After installation, use either the bash command `uhd_find_devices` or `uhd_usrp_probe` to ensure that the radios can be found. Additionally, [Docker](https://www.docker.com/) needs to be installed.

## Installation
```bash
git clone https://github.com/TylerTucker/BluesClues.git
cd BluesClues/docker
docker build -t bluesclues .
```

# Running

To allow the docker container to access USB devices, we pass the USB device folder to the container. Once the container opens, follow the usage instructions.

```bash
docker run -it --device=/dev/bus/usb:/dev/bus/usb bluesclues /bin/bash
```

If this is the first use of the Ubertooth, the btbr firmware must be loaded to it. If not, this step should be skipped. Please note that the Ubertooth will need to be unplugged from USB, then plugged back in to power cycle. The docker container may need to restart to access the Ubertooth in this case.

```bash  
# Program Ubertooth
cd /BluesClues/ubertooth/src/firmware/btbr
ubertooth-dfu -d btbr.dfu -r
```
We need to run two programs simultaneously to achieve full de-anonymization. Using a tmux session, we run the btsniffer code. The, we run the Ubertooth code in the main shell.

```bash
# Run Bluetooth sniffer in a tmux session
cd btsniffer/single-board/build/
tmux new -s btsniffer
./btsniffer
# Hit 'CTRL+B', then 'D' to detach from the tmux session
# Run Ubertooth code to attach to devices identified by sniffer
cd /BluesClues/ubertooth/src/host/python/ubtbr
./ubertooth-btbr-thread
```

The ubertooth program will log device information to an SQLite file called `blues.sqlite` in the `ubtbr` directory.
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

To allow the docker container to access USB devices, we pass the USB device folder to the container. Once the container opens, follow the usage instructions. We need to run two programs simultaneously to achieve full de-anonymization. In one tmux session, we run the btsniffer code. In a second, we run the Ubertooth code.

```bash
docker run -it --device=/dev/bus/usb:/dev/bus/usb bluesclues /bin/bash
# Program Ubertooth
ubertooth-dfu -d btbr.dfu -r
# Run Bluetooth sniffer in a tmux session
tmux new -s btsniffer
./btsniffer
# Hit 'CTRL+B', then 'D' to detach from the tmux session
# Run Ubertooth code to attach to devices identified by sniffer
cd /BluesClues/ubertooth/src/host/python/ubtbr
./ubertooth-btbr-thread
```

Run ubertooth:
```
./ubertooth-btbr-thread
```

The ubertooth program will log successfully-detected devices in an SQLite file called ```blues.sqlite```

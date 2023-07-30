21e-intth-mini-project
======================
A repo for code from the Internet of Things Technology course miniproject fall
2021  

This project examines a 6LoWPAN network setup using Raspberry Pi's and
[this](https://openlabs.co/OSHW/Raspberry-Pi-802.15.4-radio) 6LoWPAN module  

TODO:
-----
* Document network structure                               -> Axel - Abhijay
   * star topology
   * linear topology
   * link local and global ipv6 address
   * any other addresses needed ?
* Header compression                                       -> Felix - Fernando
   * Plan which different cmpression types will be demonstrated
   * outline a test for each
* Network performance                                      -> Andreas - Abhijay Fernando
   * Decide on performance metrics
   * outline a test for each
   * consider routes (client-client, client-host, etc)?
* ipv4-ipv6 routing - gateway                              -> Felix - Fernando
   * talk to rune about what's actually in the project
   * ipv4 addressing schema
   * traffic generation - sensor network mock up
* Report                                                   -> Axel - Abhijay
   * outline the report
   * introduction on 6lowpan and IEEE 802.15.4

Tools and commands
------------------
This section will have example commands for some common tools used in the
project. Any general command will be given with <> around parts to be
substituted.  

### SSH (remote access)
To open a terminal on a remote machine, the following command can be used:  
``` bash
ssh <username>@<remote-address>
# i.e.
ssh test_user@123.123.123.1

# Connecting to specific port
ssh <username>@<remote-address> -p <port>
# i.e.
ssh test_user@123.123.123.1 -p 22
```
After entering the command, you will be prompted for the password for the
specified user. Please note that this needs to be a user on the remote device.

### SCP (copying files via ssh)
This command can be used copy files using the same syntax as the *cp* command:
``` bash
# copying to remote machine
scp <source_file> <user>@<remote_address>:<target_path>
# copying from remote machine
scp  <user>@<remote_address>:<source_file> <target_path>
```

Connecting to the testbed
-------------------------
The testbed will be made available via ssh on the following addresses:  
  * Gateway RPi (RaspberryPi 3):
      * Address:  77.33.35.35
      * Port:     8122
      * Username: iot1
  * RPi B slave (RaspberryPi 1):
      * Address:  77.33.35.35
      * Port:     8222
      * Username: iot2
  * RPi Zero slave:
      * Address:  77.33.35.35
      * Port:     8322
      * Username: iot3
  * WireShark Sniffer: Is currently plugged into the gateway, and can be used
                       as described below.

**OBS:** All devices use the password *au2021*

As an example, connecting to the gateway unit would be done as follows:  
``` bash
ssh iot1@77.33.35.35 -p 8122
```

Testbed configuration
---------------------
The configuration of the raspberries has now been scripted, and is invoked through either [network_setup/init_node.sh]()
or [network_setup/init_router.sh]() for the slaves and the gateway respectively.
To sync the files to the nodes use RSync as follows:
``` bash
# While in the root of this git directory
rsync -r -e --port=<ssh port> network_setup/ <node username>@<node ssh ip>:network_setup

# Example for the gateway
rsync -r -e --port=8122 network_setup/ iot1@77.33.35.35:network_setup
```
Once the scripts are syncronized, login through ssh and run them:
```bash
./network_setup/init_node.sh  # For the slaves. 
./network_setup/init_router.sh  # For the gateway
```

### Init node
This script calls the [network_setup/include/lowpan.sh]() script to configure the lowpan interfaces. the channel is hardcoded to 20,
the pan_id to fac7 and the shor_addr to the first number appearing in the hostname (i.e. 1, 2, or 3 in the current testbed).

### init router
This script first calls the lowpan setup script like the init node script does. Next it calls [network_setup/include/radvd.sh]() to setup the router advertisment daemon
advertising the network prefix fd00:da:fa7:fac::/64 as well as itself as a default route for the network.
Lastly it calls [network_setup/include/nat64.sh]() to configure tayga for NAT64 address translation under the 
prefix fd00:da:fa7:fac:a7:64::/96

### Initial installation.
The overall scripts only configure the nodes (as needed after a reboot), but first time any of the three scripts in the [network_setup/include]() folder are run, they first need to be run with the --install option. run any
of them with --help to get info on usage

Manual Configuration Description
--------------------------------
### 6LoWPAN interface
This section describes how the Raspberries used for the test bed are configured
to create a 6LoWPAN interface using the openlabs 802.15.4 radio module.

#### OS
Firstly, the Raspberry Pi's are loaded with the currently newest image of
raspbian lite, running with the kernel version 5.10.17. It's important that the
kernel version is greater than 4.7 in order to have 6LoWPAN support.

#### AT86RF233 support
Since the openlabs radio uses the Atmel AT86RF233 radio module, the kernel
module for the radio module needs to be loaded. To make this happen
automatically at startup, run the following commands:  
``` bash
if ! grep -q "dtoverlay=at86rf233" /boot/config.txt
then
        echo "dtoverlay=at86rf233" | sudo tee -a /boot/config.txt
fi
```
This adds the at86rf233 to the device tree if it's not already present.  

**OBS** The raspberry needs to be rebooted for this to take effect.

Once the device is rebooted, inspecting the loaded modules should look like
this:  
``` console
iot1@raspberrypi1:~ $ lsmod | grep at86rf230
at86rf230              28672  0
mac802154              81920  1 at86rf230
regmap_spi             16384  1 at86rf230

```
And a wpan interface should have been added as well:  

``` console
iot1@raspberrypi1:~ $ ip link show wpan0
3: wpan0: <BROADCAST,NOARP> mtu 123 qdisc noop state DOWN mode DEFAULT group default qlen 300
    link/ieee802.15.4 2a:8a:4f:d9:44:3f:8e:62 brd ff:ff:ff:ff:ff:ff:ff:ff
```

#### 6LoWPAN support
Using the normal network configuration tools, a 6LoWPAN link can now be added
onto the wpan link:  

``` bash
sudo ip link add link wpan0 name lowpan0 type lowpan
sudo ifconfig wpan0 up
sudo ifconfig lowpan0 up
```
**OBS:** Note that this step will need to be redone after a reboot. A permanent
solution will be added later.

Having reached this step on two units, ping6 should be able to work via the
6LoWPAN link:

```console
ping6 fe80::48e3:b09c:248f:c76f%lowpan0 -c1
PING fe80::48e3:b09c:248f:c76f%lowpan0(fe80::48e3:b09c:248f:c76f%lowpan0) 56 data bytes
64 bytes from fe80::48e3:b09c:248f:c76f%lowpan0: icmp_seq=1 ttl=64 time=23.0 ms

--- fe80::48e3:b09c:248f:c76f%lowpan0 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 22.995/22.995/22.995/0.000 ms
```
where *fe80::48e3:b09c:248f:c76f* is the ipv6 address of another configured
device in the PAN

#### 6LoWPAN user space tools
in order to be able to configure the lowpan stack, the wpan tools package is
fetched from git, compiled, and installed:  
``` bash
sudo apt install -y git dh-autoreconf libnl-3-dev libnl-genl-3-dev
git clone https://github.com/linux-wpan/wpan-tools.git
cd wpan-tools
./autogen.sh
# Make sure to check the output of previous command for errors.
./configure CFLAGS='-g -O0' --prefix=/usr --sysconfdir=/etc --libdir=/usr/lib
make
sudo make install
```

If successfull, the commands *iwpan*, *wpan-ping*, among others are now
available. To test this, set the pan id of the network to *0xfac7* (arbitrary
  example), and configure a short address (needs to be unique in the pan):  
``` bash
sudo ip link set lowpan0 down
sudo ip link set wpan0 down
sudo iwpan dev wpan0 set pan_id 0xfac7
sudo iwpan dev wpan0 set short_addr 0x0001
sudo ip link set wpan0 up
sudo ip link set lowpan0 up
```

### 802.15.4 Sniffer (nRF52840 Dongle)
This section describes setting up a computer to capture 802.15.4 traffic using
the nRF52840 dongle. Since there's no issue in sniffing from one of the node
computers, the second raspberry pi in the testbed is configured for sniffing.
At a later time, a seperate computer can be setup for sniffing, in case any
tests require sniffing at specific locations (Investigating the hidden node
problem for example).  

#### Dongle firmware
Firstly the dongle is flashed with the correct firmware using the windows tool
described [here](https://infocenter.nordicsemi.com/index.jsp?topic=%2Fsdk_tz_v4.1.0%2Fnrf802154_sniffer.html).  

#### Installing wireshark on the sniffing computer.
In order to capture packets, WireShark is installed. This can be done from apt:  
``` bash
sudo apt install -y wireshark tshark
```
When prompted if non-root users should be able to capture packets, answer
**Yes**. After installing, add the user to the wireshark group in order to
allow packet capture. Furthermore, the dongle extcap requires the dialout group
to communicate with the dongle. For the *iot2* user that would look like this:  
```bash
sudo usermod -a -G wireshark,dialout iot2
sudo reboot
```
The reboot is required in order to apply the new user group.  

#### Installing the extcap
In order to use wireshark to perform packet captures using the dongle, an extcap
file needs to be installed into the users wireshark extcap directory.  
Note here that the directory for extcap files is platform dependent, but can be
found by running *tshark -G folders*.  
``` bash
git clone https://github.com/NordicSemiconductor/nRF-Sniffer-for-802.15.4
sudo cp nRF-Sniffer-for-802.15.4/nrf802154_sniffer/nrf802154_sniffer.py /usr/lib/arm-linux-gnueabihf/wireshark/extcap
sudo chmod +x /usr/lib/arm-linux-gnueabihf/wireshark/extcap/nrf802154_sniffer.py
```
After this, the interface /dev/ttyACMx should appear when running *tshark -D*

#### Installing python and dependencies
Since the extcap is implemented in python, a python interpreter with pyserial
needs to be setup.
``` bash
sudo apt install python-pip
pip install pyserial
```

Once this is performed and the dongle is plugged in, ts

#### Capturing traffic
Now the computer is set up to start capturing traffic. The following command
captures 802.15.4 packets from channel 20 for 10 seconds, with the sniffer at
/dev/ttyACM0, saving it to the file lowpan.pcap:  
``` bash
tshark -i /dev/ttyACM0 -w lowpan.pcap -o extcap._dev_ttyacm0.channel:20 -a duration:10
```
The capture file can then be fetched using scp and inspected in wireshark. To
view traffic live in the terminal leave out the -w flag. Filters can either be
applied with the -f flag, or as a display filter when inspecting the capture in
wireshark.

#### Iperf
In order to test the bandwidth in the network, iperf can be used. This program
provides server and client programs to test bandwidth of tcp, udp, or sctp. The
iperf package is installed via apt:  
``` bash
sudo apt install -y iperf
```

To test a given connection, run the server command on one side of the connection:  
``` bash
iperf -V -s
```
where *-V* indicates ipv6, and *-s* is for server.  
On the other end of the connection the client command is invoked to test and
generate a report:  
``` bash
iperf -V -c <ip of server>
```
Note here that iperf doesn't support link local ipv6 addresses, so  a global
unicast address needs to be added to the devices (some 2000::/3 address), of
which an example is shown below:  
```bash
sudo ip a add dev lowpan0 2021::1/64
```

Below is an example of a bandwidth test from iot3 to iot1:  
``` console
iot3@raspberrypi3:~ $ iperf -V -c 2021::1
------------------------------------------------------------
Client connecting to 2021::1, TCP port 5001
TCP window size: 43.8 KByte (default)
------------------------------------------------------------
[  3] local 2021::3 port 33828 connected with 2021::1 port 5001
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0-10.1 sec  68.4 KBytes  55.7 Kbits/sec
```
### Tayga for gateway

You will need to select an unused /96 from your site's IPv6 address range which will be used as the NAT64 prefix. You will also need a block of unused IPv4 addresses for the dynamic address pool. TAYGA will assign IPv4 addresses from this pool to the IPv6 hosts that need NAT64 service. The dynamic pool can be chosen from private IPv4 address space (10.x.x.x, 192.168.x.x, etc) and can be of any size, although it needs to be large enough to contain one IPv4 address for every IPv6 host that needs to use the NAT64.

TAYGA also needs its own IPv4 address, but this can be taken from the dynamic address pool.

```bash
# ./configure && make && make install
# mkdir -p /var/db/tayga
# cat >/usr/local/etc/tayga.conf <<EOD
tun-device nat64
ipv4-addr 192.168.255.1                  (this is TAYGA's IPv4 address, not your router's address)
prefix 2001:db8:1:ffff::/96              (replace with an unused /96 prefix from your site's address range)
dynamic-pool 192.168.255.0/24
data-dir /var/db/tayga
EOD
# tayga --mktun
# ip link set nat64 up
# ip addr add 192.168.0.1 dev nat64      (replace with your router's IPv4 address)
# ip addr add 2001:db8:1::1 dev nat64    (replace with your router's IPv6 address)
# ip route add 192.168.255.0/24 dev nat64
# ip route add 2001:db8:1:ffff::/96 dev nat64
# tayga
# ping6 2001:db8:1:ffff::192.168.0.1
```

If the ping6 command succeeds, TAYGA is working. Now you'll need to set up NAT44 rules in iptables or elsewhere on your network so the dynamic pool addresses can reach the rest of the Internet. 

--------   
Links
http://www.litech.org/tayga/                                       
                                       
-----
                                       
### Overleaf
The report for this project will be written in
[this](https://www.overleaf.com/project/6163f758ba65ec82ecaab4db) overleaf
project  

### Jenkins serverssh iot2@andreasahn.asuscomm.com -p 8092

There is a jenkins build server [here](http://andreasahn.duckdns.org:8080/)  

### Google drive
The google drive folder (for the class) is
[here](https://drive.google.com/drive/folders/1yzeGbGf_MRgC_Fh5KQ0lFaJo75p1DVbX?usp=sharing)

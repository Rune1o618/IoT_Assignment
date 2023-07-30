#!/usr/bin/bash    

# TODO: Add pan id as an optional input parameter

show_help_text() {
    echo "Usage: $0 --init <node_number> <802.15.4 channel>"
    echo "       $0 --delete"
    echo "       $0 --install"
}

verlte() {
    [  "$1" = "`echo -e "$1\n$2" | sort -V | head -n1`" ]
}

install_lowpan() {
    # Check that kernel release is >= 4.7
    if ! verlte "4.7" $(uname -r)
    then
        echo "Lowpan is only supported on kernels >= 4.7"
        exit -1
    fi
    # Add kernel support for AT86RF233 radio module
    if ! grep -q "dtoverlay=at86rf233" /boot/config.txt
    then
        # Add to config and load manually to avoid having to reboot
        echo "dtoverlay=at86rf233" | sudo tee -a /boot/config.txt
        sudo modprobe -a  at86rf230
        echo "Loaded kernel at86rf230 kernel module"
    fi
    
    # Check if iwpan is installed
    if ! iwpan > /dev/null 2>&1
    then
        sudo apt install -y git dh-autoreconf libnl-3-dev libnl-genl-3-dev
        rm -fr wpan-tools
        git clone https://github.com/linux-wpan/wpan-tools.git
        cd wpan-tools
        if ! ./autogen.sh
        then
            echo "wpan-tools build failed"
            exit -1
        fi
        ./configure CFLAGS='-g -O0' --prefix=/usr --sysconfdir=/etc --libdir=/usr/lib
        make
        sudo make install
        cd ..
    fi
}

init_lowpan () {
    # Configure lowpan interface
    sudo ip link set lowpan0 down > /dev/null 2>&1
    sudo ip link set wpan0 down > /dev/null 2>&1
    sudo iwpan phy phy0 set channel 0 "$2"
    sudo iwpan dev wpan0 set pan_id 0xfac7
    sudo iwpan dev wpan0 set short_addr "0x$1"
    sudo ip link add link wpan0 name lowpan0 type lowpan
    sudo ip link set wpan0 up
    sudo ip link set lowpan0 up
}

delete_lowpan() {
    # Delete lowpan interfaces
    sudo ip link delete lowpan0
    # The wpan interface canot be deleted
    # It's taken down instead
    sudo ip link set wpan0 down

    # wpan tools are left installed

    # So is the kernel module and config.
}

if [[ $# -ge 1 ]]
then 
    if [[ $1 == "--delete" ]]
    then
        if [[ $# -eq 1 ]]
        then 
            delete_lowpan && echo "Lowpan interfaces deleted"
            exit 0
        else
            echo "--delete takes no arguments"
            show_help_text
            exit -1
        fi
    elif [[ $1 == "--install" ]]
    then
        if [[ $# -eq 1 ]]
        then 
            install_lowpan && echo "Lowpan tools and drivers installed"
            exit 0
        else
            echo "--install takes no arguments"
            show_help_text
            exit -1
        fi
    elif [[ $1 == "--init" ]]
    then
        if [[ $# -eq 3 ]]
        then 
            init_lowpan $2 $3
            exit 0
        else
            echo "--init takes 2 arguments"
            show_help_text
            exit -1
        fi
    else
        echo "Invalid command argument"
        show_help_text
        exit -1
    fi
else
    show_help_text
    exit -1
fi

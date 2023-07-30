#!/usr/bin/bash 

show_help_text(){
    echo "Usage: $0 --install <64 bit network prefix>"
    echo "       $0 --remove"
    echo "example: $0 --install fd00:da:fa7:fac::/64"
}

install_radvd() {
    prefix=$1

    # Check that lowpan0 exists
    if ! ip a | grep -q "lowpan0"
    then 
        echo "A lowpan0 interface must be present"
        exit -1
    fi

    # kill any running radvd
    sudo killall radvd

    # Calculate EUI64
    eui64=$($script_dir/ip_utils.py --construct-eui64 lowpan0)

    # Construct Address (validates the prefix as well)
    ipv6_addr=$($script_dir/ip_utils.py --construct-ipv6 $prefix $eui64)

    # Install and configure radvd
    sudo apt install radvd -y
    cat $script_dir/radvd.conf | sed "s/__PREFIX__/${prefix////\\/}/g" | sed "s/__ADDR__/${ipv6_addr////\\/}/g" | sudo tee /etc/radvd.conf

    # Add ip to lowpan0 - no SLAAC for the router
    sudo ip a add "$ipv6_addr/64" dev lowpan0

    # Enable ipv6 forwarding - immediate and persistent
    sudo sh -c "echo 1 > /proc/sys/net/ipv6/conf/all/forwarding"
    sudo sed -i_bkp 's/#net\.ipv6\.conf\.all\.forwarding\=1/net.ipv6.conf.all.forwarding=1/g' /etc/sysctl.conf

    # Start radvd
    sudo radvd
}

remove_radvd(){
    # kill any running radvd
    sudo killall radvd
    
    # Disable ipv6 forwarding
    sudo sed -i_bkp 's/net\.ipv6\.conf\.all\.forwarding\=1/#net.ipv6.conf.all.forwarding=1/g' /etc/sysctl.conf
    sudo sh -c "echo 0 > /proc/sys/net/ipv6/conf/all/forwarding"

    # remove ip from lowpan0
    address=$(cat /etc/radvd.conf | awk '/abro/ {print $2}')
    sudo ip a del $address dev lowpan0

    # remove radvd
    sudo rm /etc/radvd.conf
    sudo apt remove radvd -y
}

if [[ $# -ge 1 ]]
then 
    script_dir=$(dirname $0)
    if [[ $1 == "--install" ]]
    then
        if [[ $# -eq 2 ]]
        then 
            install_radvd $2 && echo "radvd installed with prefix $2"
            exit 0
        else
            echo "--install takes 1 argument"
            show_help_text
            exit -1
        fi
    elif [[ $1 == "--remove" ]]
    then
        if [[ $# -eq 1 ]]
        then
            remove_radvd && echo "Removed radvd"
            exit 0
        else
            echo "--remove takes no arguments"
            show_help_text
            exit -1
        fi
    else
        echo "Invalid command argument $1"
        show_help_text
        exit -1
    fi
else
    show_help_text
    exit -1
fi

#!/usr/bin/bash 

show_help_text(){
    echo "Usage: $0 --install <96 bit ipv6 network nat64_prefix> <ipv4 address pool> <ext iface>"
    echo "       $0 --remove"
    echo "example: $0 --install fd00:da:fa7:fac:a7/96 192.168.2.80/29 eth0"
}

install_tayga(){
    # Check specified prefix
    nat64_prefix=$1
    if ! $script_dir/ip_utils.py --check-ip $nat64_prefix $nat64_prefix
    then
        echo "The provided network prefix is invalid"
        exit -1
    fi
    if ! [[ ${nat64_prefix:${#nat64_prefix}-3:3} == "/96" ]]
    then
        echo "The IPv6 prefix must be 96 bits"
        exit -1
    fi

    # Derive corresponding ipv6 address
    ipv6_subnet=$($script_dir/ip_utils.py --network-from-address $nat64_prefix /64)
    ipv6_addr=$($script_dir/ip_utils.py --get-ip all $ipv6_subnet)
    if [ -z "$ipv6_addr" ]
    then
        echo "No valid IPv6 address with the /64 version of the given prefix."
        exit -1
    fi

    # Check specified ipv4 address pool
    ipv4_pool=$2
    if ! $script_dir/ip_utils.py --check-ip $ipv4_pool $ipv4_pool
    then
        echo "The provided ipv4 pool is invalid"
        exit -1
    fi

    # construct corresponding ipv4 address
    ipv4_addr=$(echo $ipv4_pool | sed -E 's/([0-9]+\.[0-9]+\.[0-9]+.[0-9]*)0\/[0-9]+/\11/g')
    if [ -z "$ipv4_addr" ]
    then
        echo "No valid IPv4 address in the specified pool could be constructed."
        exit -1
    fi

    # Fetch external ipv4
    ext_ipv4=$($script_dir/ip_utils.py --get-ip $3 0.0.0.0/0)
    if [ -z "$ext_ipv4" ]
    then
        echo "No valid IPv4 found on specified external interface"
        exit -1
    fi


    # Install tayga
    sudo apt install -y tayga

    # Make a db dir
    sudo mkdir -p /var/db/tayga

    # Add a config file
    cat $script_dir/tayga.conf | sed "s/__IPV4_ADDR__/${ipv4_addr////\\/}/g" | sed "s/__PREFIX__/${nat64_prefix////\\/}/g" | sed "s/__IPV4_POOL__/${ipv4_pool////\\/}/g" | sudo tee /usr/local/etc/tayga.conf

    # Configure tayga interface
    sudo tayga --mktun
    sudo ip link set nat64 up
    sudo ip addr add $ext_ipv4 dev nat64
    sudo ip addr add $ipv6_addr dev nat64
    sudo ip route add $ipv4_pool dev nat64
    sudo ip route add $nat64_prefix dev nat64

    # Add ip6tables 
    sudo ip6tables -A FORWARD -s $ipv6_subnet -j ACCEPT

    # Start tayga daemon
    sudo tayga -c /usr/local/etc/tayga.conf

    exit 0
}


remove_tayga(){
    sudo killall tayga
    sudo ip link delete nat64
    sudo rm -f /usr/local/etc/tayga.conf
    sudo rm -fr /var/db/tayga
    sudo apt remove tayga -y
    echo "Tayga removed"
    exit 0
}

if [[ $# -ge 1 ]]
then 
    script_dir=$(dirname $0)
    if [[ $1 == "--install" ]]
    then
        if [[ $# -eq 4 ]]
        then 
            install_tayga $2 $3 $4 && echo "tayga nat64 installed with prefix $2 and dynamic address pool $3"
            exit 0
        else
            echo "--install takes 3 arguments"
            show_help_text
            exit -1
        fi
    elif [[ $1 == "--remove" ]]
    then
        if [[ $# -eq 1 ]]
        then
            remove_tayga && echo "Removed tayga nat64"
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

#! /bin/bash

script_dir=$(dirname $0)
$script_dir/init_node.sh
$script_dir/include/radvd.sh --install fd00:da:fa7:fac::/64
$script_dir/include/nat64.sh --install fd00:da:fa7:fac:a7:64::/96 192.168.1.40/29 eth0
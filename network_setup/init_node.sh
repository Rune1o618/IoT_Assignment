#! /bin/bash

script_dir=$(dirname $0)
host_number=$(hostname | grep -Eo '[0-9]+')

$script_dir/include/lowpan.sh --init $host_number 20
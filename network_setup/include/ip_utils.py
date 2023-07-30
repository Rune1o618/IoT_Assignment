#! /usr/bin/python3
import re
import sys
import subprocess
import ipaddress
import os
from typing import List, Tuple


def show_help():
    cmd = sys.argv[0].split('/')[-1]
    print(f'Usage: 1) {cmd} --construct-eui64 <iface>\r\n'
           '          Get the MAC address of the specified device and construct\r\n'
           '          an EUI64 from it\r\n'  
          f'          example: {cmd} --construct-eui64 eth0\r\n'          
          f'       2) {cmd} --check-ip <ip> [range]\r\n'
           '          Check if the given ip, and optionally if it is in the specified range.\r\n'
          f'          example: {cmd} --check-ip 192.168.1.82 192.168.1.80/29\r\n'
          f'       3) {cmd} --get-ip <iface> [range]\r\n'
           '          Get an IP(v4/v6) from the specied interface, optionally constricting the options to \r\n'
           '          a specific subnet/range. Use the keyword \'all\' for the iface to search all ifaces.\r\n'
           '          First match if several exist.\r\n'
          f'          example: {cmd} --get-ip all\r\n'
          f'          example: {cmd} --get-ip eth0 192.168.1.0/24\r\n'
          f'       4) {cmd} --network-from-address <IP address> <netmask>\r\n'
           '          Create a valid network specification from an adress and the size of the containing subnet.'
          f'          example: {cmd} --network-from-address 192.168.1.82 24' 
          f'       5) {cmd} --construct-ipv6 <prefix> <EUI64>\r\n'
           '          Construct and validate an IPv6 address from the provided prefix and '
          f'       6) {cmd} --help/-h \r\n'
           '          Show this message\r\n'
    )


def _regex_from_iface_info(iface: str, pattern: str) -> List[str]:
    if_info = subprocess.getoutput(f'ip a show {iface}')
    return re.findall(pattern, if_info.replace('\n', ' '))


def construct_eui64(iface: str) -> str:
    MAC_REGEX = '.*link/[^\s]+ ([a-z0-9:]+) brd'
    mac = _regex_from_iface_info(iface, MAC_REGEX)
    try:
        mac_bytes = bytes([int(e, 16) for e in mac[0].split(':')])
    except (IndexError, AttributeError):
        exit(os.EX_DATAERR)
    eui64_bytes = bytes((mac_bytes[0] ^ 0x2,)) + mac_bytes[1:]
    if len(mac_bytes) == 6:
        eui64_bytes = eui64_bytes[:3] + bytes((0xff, 0xfe)) + eui64_bytes[3:]
    elif len(mac_bytes) != 8:
        print(f'Unexpected mac length of {len(mac_bytes)} bytes')
        exit(os.EX_DATAERR)
    return ':'.join([eui64_bytes[2*i:2*i+2].hex() for i in range(4)])


def check_ip(ip: str, ip_range: str) -> int:
    result_str = ''
    try:
        address = ipaddress.ip_address(ip)
        result_str += f'{ip} is a valid IPv{address.version} address'
    except ValueError as e:
        print(f'{ip} is not a valid IP address: {e}')
        return os.EX_USAGE
    if ip_range is not None:
        try:
            network = ipaddress.ip_network(ip_range)
            if address not in network:
                print(f'{ip} is not in the subnet {ip_range}')
                return os.EX_DATAERR
            else:
                result_str += f' in the subnet {ip_range}'
        except ValueError as e:
            print(f'The provided range is not a valid ip subnet specifier: {e}')
            return os.EX_USAGE
    print(result_str)
    return os.EX_OK


def get_ip(iface: str, ip_range: str) -> Tuple[str, str]:
    IP_REGEX = r' inet[6]{0,1} ([0-9a-f:.]+)/([0-9]+) '

    # Search all interfaces if keyword 'all' is provided
    if iface == 'all': iface = ''  
    ip_matches = _regex_from_iface_info(iface, IP_REGEX)

    if ip_range is not None:
        try:
            network = ipaddress.ip_network(ip_range)
            ip_matches = [(ip, netmask) for ip, netmask in ip_matches 
                          if ipaddress.ip_address(ip) in network]
        except ValueError as e:
            print(f'Invalid ip/range: {e}')
            exit(os.EX_USAGE)
        
    try:
        return ip_matches[0]
    except IndexError:
        exit(os.EX_DATAERR)


def network_from_ip(ip: str, netmask: str) -> str:
    return ipaddress.ip_network((ip.split('/')[0], int(netmask.split('/')[1])), strict=False)
    

def construct_address(prefix: str, eui64: str) -> str:
    try:
        prfx = ipaddress.ip_network(prefix)
        if prfx.prefixlen > 64:
            print('The supplied prefix must have a netmask of len <= 64')
            exit(os.EX_DATAERR)
        if not prfx.version == 6:
            print("The specified prefix must be IPv6")
            exit(os.EX_DATAERR)
        addr = ipaddress.ip_address(':'.join(prfx.network_address.exploded.split(':')[:4] + [eui64]))
        return addr.compressed
    except (ValueError, AttributeError, IndexError) as e:
        print(f'Failed to construct address: {e}')
        exit(os.EX_DATAERR)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        if sys.argv[1] in ['--help', '-h']:
            show_help()
        elif sys.argv[1] == '--construct-eui64':
            if len(sys.argv) == 3:
                eui64 = construct_eui64(sys.argv[2])
                print(eui64)
                exit(os.EX_OK)
            else:
                print('--construct-eui64 takes exactly 1 argument')
                show_help()
                exit(os.EX_USAGE)
        elif sys.argv[1] == '--check-ip':
            if len(sys.argv) in [3, 4]:
                ip = sys.argv[2].split('/')[0]  # This strips subnet indications
                ip_range = None
                if len(sys.argv) == 4:
                    ip_range = sys.argv[3]
                exit(check_ip(ip, ip_range))
            else:
                print('--check-ip takes 1 or 2 argument(s).')
                show_help()
                exit(os.EX_USAGE)
        elif sys.argv[1] == '--get-ip':
            if len(sys.argv) in [3, 4]:
                iface = sys.argv[2]
                ip_range = None
                if len(sys.argv) == 4:
                    ip_range = sys.argv[3]
                address_and_netmask = get_ip(iface, ip_range)
                if address_and_netmask is None:
                    exit(os.EX_DATAERR)
                print(address_and_netmask[0])
                exit(os.EX_OK)
            else:
                print('--get-ip command takes 1 or 2 argument(s)')
                show_help()
                exit(os.EX_USAGE)
        elif sys.argv[1] == '--network-from-address':
            if len(sys.argv) == 4:
                network = network_from_ip(sys.argv[2], sys.argv[3])
                print(network)
                exit(os.EX_OK)
            else:
                print('--network-from-address command takes 2 arguments')
                show_help()
                exit(os.EX_USAGE)
        elif sys.argv[1] == '--construct-ipv6':
            if len(sys.argv) == 4:
                address = construct_address(sys.argv[2], sys.argv[3])
                print(address)
                exit(os.EX_OK)
            else:
                print('--construct-ipv6 command takes 2 arguments')
                show_help()
                exit(os.EX_USAGE)
        else:
            print(f'Unrecognized command {sys.argv[1]}')
            show_help()
            exit(os.EX_USAGE)
    else:
        show_help()
        exit(os.EX_USAGE)

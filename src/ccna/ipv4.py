from pprint import pprint
import json
import ipaddress


def binary_to_decimal(ip_binary: str) -> ipaddress.IPv4Address:
    """Converts IPv4 Binary Form to Decimal Form

    Args:
        ip_binary (str): IPv4 in Binary Form. This should not include the dot separators and the length
            must be equal to 32 (IPv4 32 Bit). Example: '11000000101010000000000100000001'

    Returns:
        ipaddress.IPv4Address: IPv4Address object in Decimal Form
    """
    assert len(ip_binary) == 32
    
    decimal_rep = int(ip_binary, 2)
    return ipaddress.IPv4Address(decimal_rep)


def decimal_to_binary(ip_decimal: str) -> str:
    """Converts IPv4 Decimal Form to Binary Form

    Args:
        ip_decimal (str): IPv4 in Decimal Form.

    Returns:
        str: IPv4 Binary Form. Does not include dot separators.
    """
    address = ipaddress.IPv4Address(ip_decimal)
    binary_str = ''.join(f'{octet:08b}' for octet in address.packed)
    return binary_str


def num_of_bits(ip_decimal: str) -> int:
    """Calculates the Number of Bits from IPv4 (Decimal Form)

    Args:
        ip_decimal (str): IPv4 in Decimal Form (e.g. '192.168.1.1')

    Returns:
        int: Number of Bits
    """
    ip_binary = decimal_to_binary(ip_decimal)
    return sum(int(c) for c in ip_binary)


def get_network_address(host_ipv4: str, subnet_mask: str) -> ipaddress.IPv4Address:
    """Returns the Network Address of a given Host IPv4 and Subnet Mask

    Args:
        host_ipv4 (str): Host IPv4 (e.g. '10.5.4.100')
        subnet_mask (str): Subnet Mask (e.g. '255.255.255.0')

    Returns:
        str: Network Address of the Host with a Subnet
    """

    host_ipv4_int = int(ipaddress.IPv4Address(host_ipv4))
    subnet_mask_int = int(ipaddress.IPv4Address(subnet_mask))
    
    return ipaddress.IPv4Address(host_ipv4_int & subnet_mask_int)


def num_of_subnets(num_subnet_bits: int) -> int:
    """Number of Subnets from a given Number of Subnet Bits

    Args:
        num_subnet_bits (int): Number of Subnet Bits (Size)

    Returns:
        int: Number of Subnets
    """
    return 2 ** num_subnet_bits


def num_of_hosts(num_host_bits: int) -> int:
    """Number of Hosts from given Number of Host Bits

    Args:
        num_host_bits (int): Number of Host Bits (Size)

    Returns:
        int: Number of Hosts
    """
    return (2 ** num_host_bits) - 2


def get_subnet_from_new_mask(host_ipv4: str, orig_subnet_mask: str, new_subnet_mask: str):
    num_new_subnet_bits = num_of_bits(new_subnet_mask)
    num_orig_subnet_bits = num_of_bits(orig_subnet_mask)
    num_subnet_bits = num_new_subnet_bits - num_orig_subnet_bits  #<-- Number of Bits Borrowed
    
    num_subnets = 2 ** num_subnet_bits
    num_host_bits = 32 - num_new_subnet_bits
    num_hosts = (2 ** num_host_bits) - 2
    
    new_network_address = ipaddress.IPv4Network(f'{get_network_address(host_ipv4, new_subnet_mask)}/{num_new_subnet_bits}')
    
    return {
        "Number of Original Subnet's Bits": num_orig_subnet_bits,
        "Number of New Subnet's Bits": num_new_subnet_bits,
        "Number of Subnet Bits": num_subnet_bits,
        "Number of Subnets": num_subnets,
        "Number of Host Bits": num_host_bits,
        "Number of Hosts": num_hosts,
        "Network Address of this Subnet": str(new_network_address.network_address),
        "IPv4 Address of First Host on this Subnet": str(new_network_address[1]),
        "IPv4 Address of Last Host on this Subnet": str(new_network_address[-1] - 1),
        "IPv4 Broadcast Address on this Subnet": str(new_network_address.broadcast_address),
    }


def subnet_mask_address(subnet_num_of_bits: int) -> ipaddress.IPv4Address:
    """Calculates Subnet Mask Address.

    Args:
        subnet_num_of_bits (int): Number of Bits in the Subnet

    Returns:
        ipaddress.IPv4Address: Subnet Mask Address
    """
    return ipaddress.IPv4Network(f'0.0.0.0/{subnet_num_of_bits}', strict=False).netmask

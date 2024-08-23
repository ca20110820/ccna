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
    num_subnet_bits = num_new_subnet_bits - \
        num_orig_subnet_bits  # <-- Number of Bits Borrowed

    num_subnets = 2 ** num_subnet_bits
    num_host_bits = 32 - num_new_subnet_bits
    num_hosts = (2 ** num_host_bits) - 2

    new_network_address = ipaddress.IPv4Network(
        f'{get_network_address(host_ipv4, new_subnet_mask)}/{num_new_subnet_bits}')

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


def get_num_subnets_and_hosts(original_subnet: str, new_subnet_mask: str) -> tuple[int, int]:
    """Calculate the Number of Subnets and Hosts from Original Subnet (with CIDR Prefix) and New Subnet Mask.

    Args:
        original_subnet (str): Original Subnet with CIDR Prefix (e.g. "192.168.0.0/24").
        new_subnet_mask (str): New Subnet Mask (e.g. "255.255.255.128").

    Returns:
        tuple[int, int]: Number of Subnets and Hosts, respectively.
    """

    # Parse the original CIDR
    original_network = ipaddress.ip_network(original_subnet, strict=False)

    # Calculate the original prefix length and new prefix length
    original_prefix_len = original_network.prefixlen
    new_prefix_len = ipaddress.IPv4Network(
        f'0.0.0.0/{new_subnet_mask}').prefixlen

    # Number of subnets
    num_subnets = 2 ** (new_prefix_len - original_prefix_len)

    # Number of hosts per subnet
    num_hosts = 2 ** (32 - new_prefix_len) - 2

    return num_subnets, num_hosts


def get_subnets(subnet: str, new_subnet_mask: str) -> list[ipaddress.IPv4Network]:
    """Enumerate all Subnets from the Original Subnet (with CIDR Prefix) and New Subnet Mask.

    Args:
        subnet (str): Original Subnet (with CIDR Prefix).
        new_subnet_mask (str): New Subnet Mask.

    Returns:
        list[ipaddress.IPv4Network]: List of IPv4 Subnets.
    """
    # Create an IPv4Network object with the given network address and subnet mask
    network_obj = ipaddress.IPv4Network(subnet, strict=False)

    # Calculate the new prefix length from the subnet mask
    new_prefix_len = ipaddress.IPv4Network(
        f'0.0.0.0/{new_subnet_mask}').prefixlen

    # Get the subnets of the network with the new subnet mask
    subnets = list(network_obj.subnets(new_prefix=new_prefix_len))

    return subnets


def get_subnet_infos(subnet: str, prefix_length: int) -> tuple[ipaddress.IPv4Address, int, int]:
    """
    Calculates and enumerates subnet information based on the number of bits borrowed 
    from the host portion of an IP address.

    Args:
        subnet (str): The base subnet address (e.g., '192.168.100.0').
        prefix_length (int): The initial prefix length (e.g., 24 for a /24 subnet).

    Returns:
        list[tuple[int, str, int, int]]: A list of tuples where each tuple contains:
            - int: The number of bits borrowed from the host portion.
            - str: The resulting subnet mask.
            - int: The number of subnets created by borrowing the bits.
            - int: The number of hosts available per subnet.

    Raises:
        AssertionError: If the subnet contains a '/' character or if the prefix length
                        is not within the range [1, 32].

    Example:
        >>> get_subnet_infos('192.168.100.0', 24)
        [(1, '255.255.255.128', 2, 126),
         (2, '255.255.255.192', 4, 62),
         (3, '255.255.255.224', 8, 30),
         (4, '255.255.255.240', 16, 14),
         (5, '255.255.255.248', 32, 6),
         (6, '255.255.255.252', 64, 2)]
    """
    assert "/" not in subnet, "Subnet Address cannot contain '/'"
    assert 1 <= prefix_length <= 32, "Prefix Length must be in [1, 32]"

    # Initialize the base network
    net = ipaddress.IPv4Network(f'{subnet}/{prefix_length}')

    results = []

    # Loop over the number of bits to borrow (from 1 to 6, because 24+6 = 30)
    for bits in range(1, (30 - prefix_length) + 1):
        # Calculate the new prefix length
        new_prefix = net.prefixlen + bits
        # Calculate the subnet mask
        subnet_mask = ipaddress.IPv4Network(f'0.0.0.0/{new_prefix}').netmask
        # Calculate the number of subnets
        num_subnets = 2 ** bits
        # Calculate the number of hosts per subnet
        num_hosts = (2 ** (32 - new_prefix)) - 2

        # Append the result as a tuple (subnet_mask, num_subnets, num_hosts)
        results.append((bits, str(subnet_mask), num_subnets, num_hosts))

    return results


def get_vlsm_optimal_subnets(orig_addr: str, orig_cidr: int, subnet_required_hosts: list[int]) -> list[dict]:
    """Finds the Optimal VLSM Subnets of a given IPv4 and Required Number of Hosts of each subnet.

    Args:
        orig_addr (str): Original IPv4 Address.
        orig_cidr (int): Original Network's CIDR (e.g. /24).
        subnet_required_hosts (list[int]): List of Required Number of Hosts for each Subnet.

    Returns:
        list[dict]: New Subnets with their IP Address and Range Information.
    """
    # Sort the `subnet_required_hosts` from largest to smallest (descending).
    subnet_required_hosts.sort(reverse=True)

    # Convert the original address to an IPv4 network object
    orig_network = ipaddress.IPv4Network(f'{orig_addr}/{orig_cidr}', strict=False)
    
    subnets = []
    current_base_address = orig_network.network_address

    for hosts in subnet_required_hosts:
        # Find the "Fulfiller's" Prefix Length
        required_prefix_length = 32 - (hosts - 1).bit_length()
        
        # Calculate the Num of Host Bits (= 32 bits - Fulfiller's Prefix Length)
        num_host_bits = 32 - required_prefix_length
        
        # Calculate the Block Size (= 2 ^ Num of Host Bits)
        block_size = 2 ** num_host_bits

        # Create the subnet with the current base address and calculated prefix length
        new_subnet = ipaddress.IPv4Network(f'{current_base_address}/{required_prefix_length}', strict=False)

        # Extract the IP Range from the Subnet's IP Address
        subnet_info = {
            "subnet": str(new_subnet.network_address),
            "prefix_length": required_prefix_length,
            "network": str(new_subnet),
            "first_host": str(new_subnet.network_address + 1),
            "last_host": str(new_subnet.broadcast_address - 1),
            "broadcast": str(new_subnet.broadcast_address),
            "total_hosts": new_subnet.num_addresses,
            "usable_hosts": new_subnet.num_addresses - 2
        }
        subnets.append(subnet_info)

        # Update the current base address for the next subnet
        current_base_address = new_subnet.broadcast_address + 1

    return subnets

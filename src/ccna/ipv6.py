import ipaddress


def compress_ipv6(ipv6_address: str) -> str:
    """Compress the given IPv6 Address.

    Args:
        ipv6_address (str): IPv6 Address (not in CIDR notation).

    Returns:
        str: Compressed IPv6.
    """
    return str(ipaddress.IPv6Address(ipv6_address))


def decompress_ipv6(ipv6_address: str) -> str:
    """Decompress the given IPv6 Address.

    Args:
        ipv6_address (str): IPv6 Address (not in CIDR notation).

    Returns:
        str: Decompressed IPv6.
    """
    return str(ipaddress.IPv6Address(ipv6_address).exploded)


def get_subnets(starting_subnet: str, num_subnets: int) -> list[str]:
    """List IPv6 Subnets from a given starting IPv6 Subnet Address.

    Args:
        ipv6_address (str): Starting IPv6 Subnet (not in CIDR notation).
        prefix_length (int): Prefix Length of the Starting IPv6 Subnet.
        num_subnets (int): Number of Required Subnets.

    Returns:
        list[dict]: List of Subnets.
    """
    # Create an IPv6 network object
    network = ipaddress.IPv6Network(starting_subnet)
    
    # Generate subnets by increasing the prefix length by 1
    subnets = list(network.subnets(new_prefix=network.prefixlen + 1))[:num_subnets]
    
    # Return the list of derived subnets
    return [str(subnet) for subnet in subnets]


def derive_subnets(starting_subnet, count) -> list[str]:
    """Derive a specified number of IPv6 subnets from a given starting IPv6 subnet address.

    This function generates a list of new IPv6 subnets by incrementing the fourth segment
    of the provided starting subnet. It ensures that the new subnets remain within the valid
    range for IPv6 addresses.

    Args:
        starting_subnet (str): The starting IPv6 subnet in CIDR notation (e.g., '2001:db8::/64').
        count (int): The number of subnets to derive from the starting subnet.

    Raises:
        ValueError: If the resulting subnet exceeds the valid range for the fourth segment of IPv6 addresses.

    Returns:
        list[str]: A list of derived IPv6 subnets in CIDR notation, each with a /64 prefix.
    """
    # Create an IPv6 network object from the starting subnet
    network = ipaddress.ip_network(starting_subnet, strict=False)
    
    # Get the base address of the network
    base = network.network_address

    # Convert the base address to a list of its segments
    base_segments = base.exploded.split(':')
    
    # Prepare a list to hold the derived subnets
    derived_subnets = []
    
    # Increment the relevant segment (4th segment in this case)
    for i in range(1, count + 1):
        # Convert the segment to an integer, increment it, and convert back to hex
        new_segment = int(base_segments[3], 16) + i
        # Ensure it stays within valid hex (up to FFFF for a segment)
        if new_segment > 0xFFFF:
            raise ValueError("Exceeded valid segment range for IPv6")
        
        # Construct the new address
        new_segments = base_segments[:3] + [format(new_segment, 'x')] + base_segments[4:]
        
        # Preserve the last 3 segments of the original address
        new_segments[-3:] = base_segments[-3:]
        
        new_address = ':'.join(new_segments)
        
        # Append the new subnet in CIDR notation
        derived_subnets.append((f"{compress_ipv6(new_address)}/64"))
    
    return derived_subnets

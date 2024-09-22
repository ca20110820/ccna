import pytest

from ccna.ipv6 import (compress_ipv6,
                       decompress_ipv6,
                       derive_subnets
                       )


def test_compress_ipv6():
    """Test the compress_ipv6 function with various IPv6 address formats.

    Test cases include:
    1. Standard IPv6 address.
    2. Address with leading zeros.
    3. Address with multiple groups of zeros.
    4. Invalid address format to ensure proper exception handling.
    """
    # Test case 1: Standard IPv6 address
    assert compress_ipv6("2001:0db8:0000:0042:0000:8a2e:0370:7334") == "2001:db8:0:42:0:8a2e:370:7334"
    
    # Test case 2: Address with leading zeros
    assert compress_ipv6("2001:0db8:0000:0000:0000:0000:0000:0001") == "2001:db8::1"
    
    # Test case 3: Address with multiple groups of zeros
    assert compress_ipv6("2001:0db8:0000:0000:0000:0000:0000:0000") == "2001:db8::"
    
    # Test case 4: Invalid address format
    with pytest.raises(ValueError):
        compress_ipv6("invalid_ipv6")


def test_decompress_ipv6():
    """Test the decompress_ipv6 function with various compressed IPv6 address formats.

    Test cases include:
    1. Compressed IPv6 address.
    2. Standard IPv6 address.
    3. Fully zero address.
    4. Invalid address format to ensure proper exception handling.
    """
    # Test case 1: Compressed IPv6 address
    assert decompress_ipv6("2001:db8::1") == "2001:0db8:0000:0000:0000:0000:0000:0001"
    
    # Test case 2: Standard IPv6 address
    assert decompress_ipv6("2001:db8:42:0:0:8a2e:370:7334") == "2001:0db8:0042:0000:0000:8a2e:0370:7334"

    # Test case 3: Fully zero address
    assert decompress_ipv6("::") == "0000:0000:0000:0000:0000:0000:0000:0000"

    # Test case 4: Invalid address format
    with pytest.raises(ValueError):
        decompress_ipv6("invalid_ipv6")


def test_derive_subnets_valid():
    """Test the derive_subnets function with valid inputs.

    Validates that the function correctly derives subnets from a given starting subnet.
    """
    result = derive_subnets('2001:db8:acad:00c8::0/64', 4)
    expected = [
        '2001:db8:acad:c9::/64',
        '2001:db8:acad:ca::/64',
        '2001:db8:acad:cb::/64',
        '2001:db8:acad:cc::/64'
    ]
    assert result == expected


def test_derive_subnets_exceeding_segment():
    """Test the derive_subnets function with exceeding segment range.

    Ensures that a ValueError is raised when attempting to derive subnets
    that exceed the valid segment range for IPv6.
    """
    with pytest.raises(ValueError, match="Exceeded valid segment range for IPv6"):
        derive_subnets('2001:0db8:85a3:ffff::/64', 2)


def test_derive_subnets_invalid_subnet():
    """Test the derive_subnets function with an invalid subnet format.

    Ensures that a ValueError is raised when an invalid subnet is provided.
    """
    with pytest.raises(ValueError):
        derive_subnets('invalid:subnet', 1)


def test_derive_subnets_single_subnet():
    """Test the derive_subnets function for generating a specific number of subnets.

    Validates that the function correctly generates a specified number of subnets
    from a given starting subnet.
    """
    # Test data
    starting_subnet = "2001:0db8:85a3:0000:0000:8a2e:0370:7334/64"
    count = 3
    expected_subnets = [
        "2001:db8:85a3:1::/64",
        "2001:db8:85a3:2::/64",
        "2001:db8:85a3:3::/64",
    ]

    result = derive_subnets(starting_subnet, count)

    assert result == expected_subnets, "Derived subnets do not match expected result"


def test_derive_subnets_no_subnets():
    """Test the derive_subnets function for no subnets to derive.

    Ensures that an empty list is returned when the count of subnets to derive is zero.
    """
    result = derive_subnets('2001:0db8:85a3:0000::/64', 0)
    expected = []
    assert result == expected

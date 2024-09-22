import unittest

from ccna.ipv4 import (get_vlsm_optimal_subnets, 
                       get_subnet_infos
                       )


class TestGetSubnetInfos(unittest.TestCase):
    def test_valid_subnet_24_prefix(self):
        """Test a standard /24 subnet."""
        result = get_subnet_infos('192.168.100.0', 24)
        expected = [
            (1, '255.255.255.128', 2, 126),
            (2, '255.255.255.192', 4, 62),
            (3, '255.255.255.224', 8, 30),
            (4, '255.255.255.240', 16, 14),
            (5, '255.255.255.248', 32, 6),
            (6, '255.255.255.252', 64, 2)
        ]
        self.assertEqual(result, expected)

    def test_valid_subnet_16_prefix(self):
        """Test a larger subnet with /16 prefix."""
        result = get_subnet_infos('172.16.0.0', 16)
        expected = [
            (1, '255.255.128.0', 2, 32766),
            (2, '255.255.192.0', 4, 16382),
            (3, '255.255.224.0', 8, 8190),
            (4, '255.255.240.0', 16, 4094),
            (5, '255.255.248.0', 32, 2046),
            (6, '255.255.252.0', 64, 1022)
        ]
        self.assertEqual(result, expected)

    def test_prefix_length_out_of_range(self):
        """Test prefix length too large."""
        with self.assertRaises(AssertionError):
            get_subnet_infos('192.168.1.0', 31)
        """Test prefix length too small."""
        with self.assertRaises(AssertionError):
            get_subnet_infos('192.168.1.0', 0)

    def test_invalid_subnet_format(self):
        """Test invalid subnet format with a '/'."""
        with self.assertRaises(AssertionError):
            get_subnet_infos('192.168.100.0/24', 24)

    def test_valid_subnet_30_prefix(self):
        """Test edge case for /30 prefix."""
        result = get_subnet_infos('10.0.0.0', 30)
        expected = []
        self.assertEqual(result, expected)

    def test_minimum_prefix_length(self):
        """Test the edge case with the smallest valid prefix length (1)."""
        result = get_subnet_infos('192.168.100.0', 1)

        expected = [
            (1, '192.0.0.0', 2, 1073741822),
            (2, '224.0.0.0', 4, 536870910),
            (3, '240.0.0.0', 8, 268435454),
            (4, '248.0.0.0', 16, 134217726),
            (5, '252.0.0.0', 32, 67108862),
            (6, '254.0.0.0', 64, 33554430),
        ]

        self.assertEqual(result, expected)


class TestVLSMOptimalSubnets(unittest.TestCase):
    def test_valid_subnets(self):
        """Test for valid subnet calculation with sufficient address space."""
        orig_addr = "192.168.1.0"
        orig_cidr = 24
        subnet_required_hosts = [50, 20, 10]
        
        expected_result = [
            {
                "subnet": "192.168.1.0",
                "prefix_length": 26,
                "network": "192.168.1.0/26",
                "first_host": "192.168.1.1",
                "last_host": "192.168.1.62",
                "broadcast": "192.168.1.63",
                "total_hosts": 64,
                "usable_hosts": 62
            },
            {
                "subnet": "192.168.1.64",
                "prefix_length": 27,
                "network": "192.168.1.64/27",
                "first_host": "192.168.1.65",
                "last_host": "192.168.1.94",
                "broadcast": "192.168.1.95",
                "total_hosts": 32,
                "usable_hosts": 30
            },
            {
                "subnet": "192.168.1.96",
                "prefix_length": 28,
                "network": "192.168.1.96/28",
                "first_host": "192.168.1.97",
                "last_host": "192.168.1.110",
                "broadcast": "192.168.1.111",
                "total_hosts": 16,
                "usable_hosts": 14
            }
        ]
        
        result = get_vlsm_optimal_subnets(orig_addr, orig_cidr, subnet_required_hosts)
        self.assertEqual(result, expected_result)

    def test_invalid_address_space(self):
        """Test that the function raises a ValueError when there's insufficient address space."""
        orig_addr = "192.168.1.0"
        orig_cidr = 30
        subnet_required_hosts = [10]  # 10 hosts need at least a /28 subnet, which is not possible with /30 network
        
        with self.assertRaises(ValueError):
            get_vlsm_optimal_subnets(orig_addr, orig_cidr, subnet_required_hosts)

    def test_empty_subnet_list(self):
        """Test that the function handles an empty subnet request list."""
        orig_addr = "192.168.1.0"
        orig_cidr = 24
        subnet_required_hosts = []
        
        expected_result = []
        result = get_vlsm_optimal_subnets(orig_addr, orig_cidr, subnet_required_hosts)
        self.assertEqual(result, expected_result)

    def test_single_subnet(self):
        """Test with a single subnet required."""
        orig_addr = "10.0.0.0"
        orig_cidr = 24
        subnet_required_hosts = [100]
        
        expected_result = [
            {
                "subnet": "10.0.0.0",
                "prefix_length": 25,
                "network": "10.0.0.0/25",
                "first_host": "10.0.0.1",
                "last_host": "10.0.0.126",
                "broadcast": "10.0.0.127",
                "total_hosts": 128,
                "usable_hosts": 126
            }
        ]
        
        result = get_vlsm_optimal_subnets(orig_addr, orig_cidr, subnet_required_hosts)
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()

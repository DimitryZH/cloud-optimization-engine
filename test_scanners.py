import unittest
from scanners.compute import scan_stopped_instances
from scanners.disks import scan_unattached_disks
from scanners.addresses import scan_unused_static_ips

class TestScanners(unittest.TestCase):
    
    def test_compute_scanner(self):
        # Mock GCP client for testing
        project_id = "test-project"
        results = scan_stopped_instances(project_id)
        self.assertEqual(len(results), 0)  # No stopped instances in test data
    
    def test_disks_scanner(self):
        project_id = "test-project"
        results = scan_unattached_disks(project_id)
        self.assertEqual(len(results), 0)  # No unattached disks in test data
    
    def test_ips_scanner(self):
        project_id = "test-project"
        results = scan_unused_static_ips(project_id)
        self.assertEqual(len(results), 0)  # No unused IPs in test data

if __name__ == '__main__':
    unittest.main()
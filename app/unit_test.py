from typing import Dict
import unittest
from pyaci import core
from vkaci_mocks import KubernetesApiMock
from graph import VkaciBuilTopology, VkaciEnvVariables, VkaciTable
from vkaci_mocks import ApicMethodsMock, create_cdp_neighbour, create_lldp_neighbour, create_cdp_no_neighbour

core.aciClassMetas = {"topRoot": {
    "properties": {}, "rnFormat": "something"}}

class TestVkaciGraph(unittest.TestCase):

    vars = {"APIC_IPS": "192.168.25.192,192.168.1.2",
            "TENANT": "Ciscolive",
            "VRF": "vrf-01",
            "MODE": "cluster",
            "KUBE_CONFIG": "$HOME/.kube/config",
            "CERT_USER": "useX509",
            "CERT_NAME": "test",
            "KEY_PATH": " 101/1/1-2"
            }

    def topology_build(self, methods:ApicMethodsMock = None, env:VkaciEnvVariables = None):
        if methods is None:
            methods = ApicMethodsMock()
        if env is None:
            env = VkaciEnvVariables(self.vars)
        return VkaciBuilTopology(
            env, methods, KubernetesApiMock())

    def test_no_env_variables(self):
        """Test that no environment variables are handled"""
        # Arange
        build = self.topology_build(env=VkaciEnvVariables({}))
        # Act
        result = build.update()
        # Assert
        self.assertIsNone(result)
        self.assertEqual(build.env.mode, 'None')
        self.assertIsNone(build.aci_vrf)
        self.assertEqual(len(build.env.apic_ip), 0)


    def test_valid_topology(self):
        """Test that a valid topology is created"""
        # Arrange
        expected = {'nodes': {'1234abc': {'node_ip': '192.168.1.2',
                                          'pods': {'dateformat': {'ip': '192.158.1.3', 'ns': 'dockerimage', 'labels': {'guest': 'frontend'}}},
                                          'bgp_peers': {'leaf-204': {'prefix_count': 2}}, 'neighbours': {'esxi4.cam.ciscolabs.com':
                                                                                                         {'switches': {'leaf-204': {'vmxnic1-eth1/1'}}, 'Description': 'VMware version 123'}},
                                          'labels': {'app': 'redis'}, 'mac': 'MOCKMO1C'}},
                    'services': {'appx': [{'name': 'example service', 'cluster_ip': '192.168.25.5', 'external_i_ps': ['192.168.5.1'],
                                           'labels': {'app': 'guestbook'}, 'prefix': '192.168.5.1/32'}]}}

        build = self.topology_build()
        # Act
        result = build.update()
    
        # Assert
        self.assertDictEqual(result, expected)
        self.assertEqual(build.aci_vrf, "uni/tn-Ciscolive/ctx-vrf-01")


    def test_valid_topology_cdpn(self):
        """Test that a valid topology is created with cdp neighbours"""
        # Arrange
        expected = {'nodes': {'1234abc': {'bgp_peers': {'leaf-204': {'prefix_count': 2}},
                                          'labels': {'app': 'redis'},
                                          'mac': 'MOCKMO1C',
                                          'neighbours': {'CiscoLabs5': {'Description': 'Cisco '
                                                                        'version '
                                                                        '123',
                                                                        'switches': {'leaf-203': {'vmxnic2-eth1/1'}}}},
                                          'node_ip': '192.168.1.2',
                                          'pods': {'dateformat': {'ip': '192.158.1.3',
                                                                  'labels': {'guest': 'frontend'},
                                                                  'ns': 'dockerimage'}}}},
                    'services': {'appx': [{'cluster_ip': '192.168.25.5',
                                           'external_i_ps': ['192.168.5.1'],
                                           'labels': {'app': 'guestbook'},
                                           'name': 'example service',
                                           'prefix': '192.168.5.1/32'}]}}

        mock = ApicMethodsMock()
        mock.lldps = [create_lldp_neighbour(False)]
        mock.cdpns = [create_cdp_neighbour(True)]
        build = self.topology_build(mock)
        # Act
        result = build.update()
        # Assert
        self.assertDictEqual(result, expected)
        self.assertEqual(build.aci_vrf, "uni/tn-Ciscolive/ctx-vrf-01")


    def test_valid_topology_no_neighbours(self):
        """Test that a valid topology is created with no neighbours"""
        # Arrange
        expected = {'nodes': {'1234abc': {'bgp_peers': {'leaf-204': {'prefix_count': 2}},
                                          'labels': {'app': 'redis'},
                                          'mac': 'MOCKMO1C',
                                          'neighbours': {},
                                          'node_ip': '192.168.1.2',
                                          'pods': {'dateformat': {'ip': '192.158.1.3',
                                                                  'labels': {'guest': 'frontend'},
                                                                  'ns': 'dockerimage'}}}},
                    'services': {'appx': [{'cluster_ip': '192.168.25.5',
                                           'external_i_ps': ['192.168.5.1'],
                                           'labels': {'app': 'guestbook'},
                                           'name': 'example service',
                                           'prefix': '192.168.5.1/32'}]}}

        mock = ApicMethodsMock()
        mock.lldps = []
        mock.cdpns = [create_cdp_no_neighbour(True)]
        build = self.topology_build(mock)
        # Act
        result = build.update()
        # Assert
        self.assertDictEqual(result, expected)
        self.assertEqual(build.aci_vrf, "uni/tn-Ciscolive/ctx-vrf-01")


    def test_leaf_table(self):
        """Test that a leaf table is correctly created"""
        # Arrange
        expected = {
            'data': [{'data': [{'data': [{'data': [{'image': 'pod.svg',
                                         'ip': '192.158.1.3',
                                                    'ns': 'dockerimage',
                                                    'value': 'dateformat'}],
                               'image': 'node.svg',
                                          'ip': '192.168.1.2',
                                          'ns': '',
                                          'value': '1234abc'}],
                     'image': 'esxi.png',
                                'interface': ['vmxnic1-eth1/1'],
                                'ns': '',
                                'value': 'esxi4.cam.ciscolabs.com'},
                               {'data': [{'image': 'node.svg',
                                          'ip': '192.168.1.2',
                                          'ns': '',
                                          'value': '1234abc'}],
                                'image': 'bgp.png',
                                'value': 'BGP peering'}],
                      'image': 'switch.png',
                      'ip': '',
                      'value': 'leaf-204'}],
            'parent': 0}

        build = build = self.topology_build()
        table = VkaciTable(build)
        # Act
        build.update()
        result = table.get_leaf_table()

        # Assert
        self.assertDictEqual(result, expected)


    def test_bgp_table(self):
        """Test that a bgp table is correctly created"""
        # Arrange
        expected = {'parent': 0, 'data': [{'value': 'leaf-204', 'ip': '', 'image': 'switch.png', 
        'data': [{'value': 'BGP Peering', 'image': 'bgp.png', 
        'data': [{'value': '1234abc', 'ip': '192.168.1.2', 'ns': '', 'image': 'node.svg'}]}, {'value': 'Prefixes', 'image': 'ip.png', 
        'data': [{'value': '0.0.0.0/0', 'image': 'route.png', 'k8s_route': 'False', 'ns': '', 'svc': '', 
        'data': [{'value': '&lt;No Hostname&gt;', 'ip': '10.4.68.5', 'image': 'Nok8slogo.png'}]}, {'value': '192.168.5.1/32', 'image': 'route.png', 'k8s_route': 'True', 'ns': 'appx', 'svc': 'example service', 
        'data': [{'value': 'leaf 203', 'ip': '192.168.2.5', 'image': 'switch.png'}, {'value': '1234abc', 'ip': '192.168.1.2', 'image': 'node.svg'}]}]}]}]}

        build = build = self.topology_build()
        table = VkaciTable(build)
        # Act
        build.update()
        result = table.get_bgp_table()

        # Assert
        self.assertDictEqual(result, expected)


    def test_node_table(self):
        """Test that a node table is correctly created"""
        # Arrange
        expected = {'parent': 0, 'data': [{'value': 'leaf-204', 'ip': '', 'image': 'switch.png', 
        'data': [{'value': 'esxi4.cam.ciscolabs.com', 'interface': ['vmxnic1-eth1/1'], 'ns': '', 'image': 'esxi.png', 
        'data': [{'value': '1234abc', 'ip': '192.168.1.2', 'ns': '', 'image': 'node.svg', 
        'data': [{'value': 'app', 'label_value': 'redis', 'image': 'label.svg'}]}]}]}]}

        build = build = self.topology_build()
        table = VkaciTable(build)
        # Act
        build.update()
        result = table.get_node_table()
        
        # Assert
        self.assertDictEqual(result, expected)


    def test_pod_table(self):
        """Test that a pod table is correctly created"""
        # Arrange
        expected = {'parent': 0, 'data': [{'value': 'leaf-204', 'ip': '', 'image': 'switch.png', 
        'data': [{'value': 'dateformat', 'ip': '192.158.1.3','ns': 'dockerimage', 'image': 'pod.svg', 
        'data': [{'value': 'guest', 'label_value': 'frontend', 'image': 'label.svg'}]}]}]}

        build = build = self.topology_build()
        table = VkaciTable(build)
        # Act
        build.update()
        result = table.get_pod_table()
       
        # Assert
        self.assertDictEqual(result, expected)


    def test_services_table(self):
        """Test that a services table is correctly created"""
        # Arrange
        expected = {'parent': 0, 'data': [{'name': 'example service', 'cluster_ip': '192.168.25.5', 'external_i_ps': ['192.168.5.1'], 
        'labels': {'app': 'guestbook'}, 'prefix': '192.168.5.1/32', 'value': 'example service', 'ns': 'appx', 
        'image': 'svc.svg', 'data': [{'value': 'app', 'label_value': 'guestbook', 'image': 'label.svg'}]}]}

        build = build = self.topology_build()
        table = VkaciTable(build)
        # Act
        build.update()
        result = table.get_services_table()
        
        # Assert
        self.assertDictEqual(result, expected)

        

if __name__ == '__main__':
    unittest.main()

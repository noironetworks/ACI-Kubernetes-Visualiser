from graph import ApicMethodsResolve
from pyaci import Node
from kubernetes import client

mock_vars = {"APIC_IPS": "192.168.25.192,192.168.1.2",
            "TENANT": "Ciscolive",
            "VRF": "vrf-01",
            "MODE": "cluster",
            "KUBE_CONFIG": "$HOME/.kube/config",
            "CERT_USER": "useX509",
            "CERT_NAME": "test",
            "KEY_PATH": " 101/1/1-2"
            }

class Expando(object):
    pass


class MockMo(object):
    def __init__(self, ip, mac, pathtDn) -> None:
        self.mac = mac
        self.fvRsCEpToPathEp = [Expando()]
        c = Expando()
        c.addr = ip
        self.Children = [c]
        self.fvRsCEpToPathEp[0].tDn = pathtDn


def create_lldp_neighbour(on: bool = True):
    n = Expando()
    n.operTxSt = n.operRxSt = "down"
    if (on):
        n.operTxSt = n.operRxSt = "up"
        n.lldpAdjEp = [Expando()]
        n.lldpAdjEp[0].sysName = "esxi4.cam.ciscolabs.com"
        n.lldpAdjEp[0].chassisIdV = "vmxnic1"
        n.lldpAdjEp[0].sysDesc = "VMware version 123"
        n.sysDesc = n.dn = "topology/pod-1/node-204"
        n.id = "eth1/1"
    return n


def create_cdp_neighbour(on: bool = False):
    n = Expando()
    n.operSt = "down"
    if (on):
        n.operSt = "up"
        n.cdpAdjEp = [Expando()]
        n.cdpAdjEp[0].sysName = "CiscoLabs5"
        n.cdpAdjEp[0].chassisIdV = n.cdpAdjEp[0].portIdV = "vmxnic2"
        n.cdpAdjEp[0].ver = "Cisco version 123"
        n.sysDesc = n.dn = "topology/pod-1/node-203"
        n.id = "eth1/1"
    return n


def create_cdp_no_neighbour(on: bool = False):
    n = Expando()
    n.operSt = "down"
    if (on):
        n.operSt = "up"
        n.cdpAdjEp = []
        n.sysDesc = n.dn = "topology/pod-1/node-203"
        n.id = "eth1/1"
    return n


def create_bgpPeer():
    b = Expando()
    b.operSt = "established"
    b.dn = "topology/pod-1/node-204"
    return b


def create_nextHop(route:str, next_hop:str, tag = "56001"):
    h = Expando()
    h.dn = "topology/pod-1/node-204/sys/uribv4/dom-calico1:vrf/db-rt/rt-["+route+"]/nh-[bgp-65002]-["+next_hop+"/32]-[unspecified]-[calico1:vrf]"
    h.addr = next_hop+"/32"
    h.tag = tag
    return h


class ApicMethodsMock(ApicMethodsResolve):
    def __init__(self) -> None:
        super().__init__()

    mo1 = MockMo("192.168.1.2", "MOCKMO1C", "pathA")
    eps = [mo1]

    lldps = [create_lldp_neighbour()]
    cdpns = [create_cdp_neighbour()]
    bgpPeers = [create_bgpPeer()]
    nextHops = [
        create_nextHop("192.168.5.1/32", "192.168.2.5"),
        create_nextHop("192.168.5.1/32", "192.168.1.2"),
        create_nextHop("0.0.0.0/0", "10.4.68.5", "65002")
        ]

    def get_fvcep(self, apic: Node, aci_vrf: str):
        return self.eps

    def get_fvcep_mac(self, apic: Node, mac: str):
        return self.eps[0]

    def get_lldpif(self, apic: Node, pathDn):
        return self.lldps

    def get_cdpif(self, apic: Node, pathDn):
        return self.cdpns

    def get_bgppeerentry(self, apic: Node, vrf: str, node_ip: str):
        return self.bgpPeers

    def get_all_nexthops(self, apic:Node, dn:str):
        return self.nextHops
    
    def path_fixup(self, apic:Node, path):
        return path
    
    def get_overlay_ip_to_switch_map(self, apic:Node):
        nodes = {"192.168.2.5":"leaf 203"}
        return nodes

    def useX509CertAuth(self, apic:Node, cert_user, cert_name, key_path):
        pass


# Fake k8s cluster data
pods = [
    client.V1Pod(
        status=client.V1PodStatus(
            host_ip="192.168.1.2", pod_ip="192.158.1.3"
        ),
        metadata=client.V1ObjectMeta(
            name="dateformat", namespace="dockerimage", labels={"guest":"frontend"}
        ),
        spec=client.V1PodSpec(
            node_name="1234abc", containers=[]
        )
    )
]

# Fake k8s cluster data for nodes
nodes = [
    client.V1Node(
        metadata=client.V1ObjectMeta(
            name="1234abc", labels = {"app":"redis"}
        )    
    )
]

# Fake k8s cluster data for services
services = [
    client.V1Service(
        metadata=client.V1ObjectMeta(
            name="example service", namespace="appx", labels = {"app":"guestbook"}
        ),
        spec=client.V1ServiceSpec(
            cluster_ip="192.168.25.5", external_i_ps=["192.168.5.1"]
        )  
    )
]

class KubernetesApiMock(object):
    '''Class to mock Kubernetes API calls'''

    def load_kube_config(self, config_file):
        return None

    def load_incluster_config(self):
        return None

    def read_namespaced_pod(self, pod, ns):
        return None

    def list_pod_for_all_namespaces(self):
        return client.V1PodList(api_version="1", items=pods)

    def list_node(self):
        return client.V1NodeList(api_version="1", items=nodes)

    def list_service_for_all_namespaces(self):
        return client.V1ServiceList(api_version="1", items=services)

    def get_cluster_custom_object(self, group, version, name, plural):
        return {'spec': {'asNumber': 56001}}
# Visualising Kubernetes ACI

## [CISCO VKACI](https://github.com/datacenter/ACI-Kubernetes-Visualiser)

## Introduction

Visualisation of Kubernetes using ACI (Vkaci) is an open-source tool that generates a cluster topology and provides a visual representation, using neo4j graph database by accessing ACI and K8s APIs. This tool lets you quickly build visualisations of K8s and ACI end to end topologies. The objective of this documentation is to outline the creation, design, and installation of Vkaci to help users view their topologies.

Cisco Application Centric Infrastructure (Cisco ACI) is a component of Cisco's purpose-based networking design, which enables data centre agility and resiliency. It creates a policy that captures higher-level business and user intent and turns it into the network constructs needed to dynamically supply network, security, and infrastructure services.

The Kubernetes API allows you to query and manipulate the state of Kubernetes API objects (For example: Pods, Namespaces, ConfigMaps, and Events).

## Licensing Requirements
### Please note

***Fundamental Requirement***

GPL 3 is a strong copyleft license, meaning that any copy or modification of the original code must also be released under the GPL v3. In other words, you can take the GPL 3’d code, add to it or make major changes, then distribute your version. However, your version is subject to the same license requirements, meaning that it must be under GPL v3 as well — anyone can see your modified code and install it for their own purposes.

***Developers Requirement***

Research indicates that open source software contributors are motivated more by a desire to learn and be part of the OSS community than by financial rewards. Hence consider distribution of this code ethically and not for any external companies production or commercial environment. 

## Installation – Helm Chart

A Helm chart for Vkaci has been created to enable simple deployment of the Vkaci app and a dependent Neo4j database along with required services on a K8s cluster.

The helm chart can currently be found in the source code for VKACI and is also available in the following repo:

<https://samiib.github.io/vkaci-chart>

**Required Variables:**

| **Name** | **Description** | **Example** |
| --- | --- | --- |
| apicIps | Comma separated list of your APIC Ips. | 10.67.185.102,10.67.185.41,10.67.185.42 |
| apicCertName | Name of the certificate configured in the APIC. | ansible.crt |
| apicKeyData | The base64 encoded string that represents the certificate data. | Steps to generate data below. |
| apicUsername | Name of the APIC certificate user. | ansible |
| vrfTenant | Tenant where the cluster VRF is deployed. | calico |
| vrfName | Name of the VRF used by the cluster. | vrf |
| n4jBrowserUrl | This will need to be set to an externally accessible URL for the Vkaci browser to reach the Neo4j service. | neo4j://192.168.2.1:30100 |

**Example values.yml:**

```yaml
# VKACI APIC Variables
apicIps: "10.67.185.102,10.67.185.41,10.67.185.42"
apicCertName: "ansible.crt"
apicKeyData: "<base64 certificate data>"
apicUsername: "ansible"
vrfTenant: "calico"
vrfName: "vrf"
# Neo4j Variables
n4jBrowserUrl: neo4j://192.168.2.1:30100
```

To generate the base64 data for apicKeyData from the apic key file use the base64 command. Eg.

```bash
base64 certificate.key
```

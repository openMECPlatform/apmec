MEA Descriptor Template Guide
=============================
Overview
--------

This document explains MEAD template structure and its various fields based
on TOSCA standards `V1.0 CSD 03 <http://docs.oasis-open.org/tosca/tosca-mec/
v1.0/tosca-mec-v1.0.html>`_.

The behavioural and deployment information of a MEA in Apmec is defined in a
template known as MEA Descriptor (MEAD). The template is based on TOSCA
standards and is written in YAML. It is on-boarded in a MEA catalog.

Each MEAD template will have below fields:

::

    tosca_definitions_version:
       This defines the TOSCA definition version on which the template is based.
       The current version being tosca_simple_profile_for_mec_1_0_0.

    tosca_default_namespace:
       This is optional. It mentions default namespace which includes schema,
       types version etc.

    description:
       A short description about the template.

    metadata:
       template_name: A name to be given to the template.

    topology_template:
       Describes the topology of the MEA under node_template field.
       node_template:
           Describes node types of a MEA.
           VDU:
               Describes properties and capabilities of Virtual Deployment
               Unit.
           CP:
               Describes properties and capabilities of Connection Point.
           VL:
               Describes properties and capabilities of Virtual Link.

For examples, please refer sample MEAD templates available at `GitHub <https:
//github.com/openstack/apmec/tree/master/samples/tosca-templates/mead>`_.

Node types
----------
A MEA includes **VDU/s**, **connection point/s** and **virtual link/s**. Hence
a valid MEAD must have these 3 components. Each component is referred as a
node and can have certain type, capabilities, properties, attributes and
requirements. These components are described under **node_templates** in the
MEAD template. **node_templates** is a child of **topology_template**.

VDU
---
Virtual Deployment Unit is a basic part of MEA. It is the VM that hosts the
network function.

:type:
    tosca.nodes.mec.VDU.Apmec
:properties:
    Describes the properties like image to be used in VDU, availability zone in
    which VDU is to be spawned, management driver to be used to manage the VDU,
    flavor describing physical properties for the VDU to be spawned, monitoring
    policies for the VDU, providing user data in form of custom commands to the
    VDU. A complete list of VDU properties currently supported by Apmec are
    listed `here <https://github.com/openstack/apmec/blob/master/apmec/tosca/
    lib/apmec_mec_defs.yaml>`_ under **properties** section of
    **tosca.nodes.mec.VDU.Apmec** field

Specifying VDU properties
^^^^^^^^^^^^^^^^^^^^^^^^^
A very simple VDU with 10 GB disk, 2 GB RAM, 2 CPUs, cirros image and in nova
availability zone can be described as:

::

  topology_template:
    node_templates:
      VDU1:
        type: tosca.nodes.mec.VDU.Apmec
        properties:
          image: cirros-0.3.5-x86_64-disk
          availability_zone: nova
        capabilities:
          mec_compute:
            properties:
              disk_size: 10 GB
              mem_size: 2048 MB
              num_cpus: 2

Using Nova flavors for VDU
^^^^^^^^^^^^^^^^^^^^^^^^^^
OpenStack specific **flavors** can also be used to describe VDU configuration.

::

  topology_template:
    node_templates:
      VDU1:
        type: tosca.nodes.mec.VDU.Apmec
        properties:
          image: cirros-0.3.5-x86_64-disk
          flavor: m1.tiny
          availability_zone: nova

However, when both **mec_compute properties** and **flavor** are mentioned in
a MEAD, **flavor** setting will take precedence.

Monitoring the VDU
""""""""""""""""""
A VDU can be monitored by pinging it on port 22 for 3 times at an interval of
2 seconds every 20 seconds. Number of retries be 6 and timeout of 2 seconds.
It can be re-spawned in case ping fails. This is described under
**monitoring_policy**.

::

    ..
      VDU1:
        type: tosca.nodes.mec.VDU.Apmec
        properties:
          monitoring_policy:
            name: ping
              parameters:
                monitoring_delay: 20
                count: 3
                interval: 2
                timeout: 2
                actions:
                  failure: respawn
                retry: 6
                port: 22

Providing user data
"""""""""""""""""""
Custom commands to be run on VDU once it is spawned can be specified in a MEAD
template as user data.

::

  ..
    VDU1:
      type: tosca.nodes.mec.VDU.Apmec
      properties:
        user_data_format: RAW
        user_data: |
          #!/bin/sh
          echo "Adding this line to demofile" > /tmp/demofile

Configuring a VDU
"""""""""""""""""
A VDU can be configured as a specific Network Function under **config**
section in MEAD template. A sample template configuring a VDU as a firewall
can be viewed in a `sample file <https://github.com/openstack/apmec/blob/
master/samples/tosca-templates/mead/tosca-config-openwrt-with-firewall.yaml>`_.

Specifying external image
"""""""""""""""""""""""""
:artifacts:
    To specify an image via a file or an external link

An image URL can be specified as **artifacts**. Apmec will specify the image
location in HOT (Heat Template) and pass it to heat-api. Heat will then spawn
the VDU with that image.

::

  ..
    VDU1:
      type: tosca.nodes.mec.VDU.Apmec
      artifacts:
        MEAImage:
          type: tosca.artifacts.Deployment.Image.VM
          file: http://download.cirros-cloud.net/0.3.5/ \
                cirros-0.3.5-x86_64-disk.img

VDU Capabilities
^^^^^^^^^^^^^^^^
Computational properties of a VDU are described as its capabilities. Allocated
RAM size, allocated disk size, memory page size, number of CPUs, number of
cores per CPU, number of threads per core can be specified.

A VDU with 10 GB disk, 2 GB RAM, 2 CPUs, 4 KB of memory page and dedicated CPU
can be specified as below. Thread and core counts can be specified as shown.

::

  ..
    VDU1:
      type: tosca.nodes.mec.VDU.Apmec
      capabilities:
        mec_compute:
          properties:
            disk_size: 10 GB
            mem_size: 2048 MB
            num_cpus: 2
            mem_page_size: small
            cpu_allocation:
              cpu_affinity: dedicated
              thread_count: 4
              core_count: 2

:capabilities:

+---------------------+---------------+-----------+--------------------------+
|Name                 |Type           |Constraints|Description               |
+---------------------+---------------+-----------+--------------------------+
|mec_compute          |Compute.       |None       |Describes the configurat  |
|                     |Container.     |           |ion of the VM on which    |
|                     |Architecture   |           |the VDU resides           |
+---------------------+---------------+-----------+--------------------------+

Compute Container Architecture
""""""""""""""""""""""""""""""
:type:
    tosca.capabilities.Compute.Container.Architecture

:properties:

+---------------+--------+--------+---------------+--------------------------+
|Name           |Required|Type    |Constraints    |Description               |
+---------------+--------+--------+---------------+--------------------------+
|mem_page_size  |No      |String  |One of below   |Indicates page size of the|
|               |        |        |               |VM                        |
|               |        |        |               |                          |
| (in MB)       |        |        |- small        |- small maps to 4 KB      |
|               |        |        |- large        |- large maps to 2 MB      |
|               |        |        |- any (default)|- any maps to system's    |
|               |        |        |               |  default                 |
|               |        |        |- custom       |- custom sets the size to |
|               |        |        |               |  specified value         |
+---------------+--------+--------+---------------+--------------------------+
|cpu_allocation |No      |CPUAllo-|               |CPU allocation requirement|
|               |        |cation  |               |like dedicated CPUs,      |
|               |        |        |               |socket/thread count       |
+---------------+--------+--------+---------------+--------------------------+
|numa_node_count|No      |Integer |               |Symmetric count of NUMA   |
|               |        |        |               |nodes to expose to VM.    |
|               |        |        |               |vCPU and Memory is split  |
|               |        |        |               |equally across this       |
|               |        |        |               |number of NUMA            |
+---------------+--------+--------+---------------+--------------------------+
|numa_nodes     |No      |Map of  |Symmetric      |Asymmetric allocation of  |
|               |        |NUMA    |numa_node_count|vCPU and memory across    |
|               |        |        |should not be  |the specified NUMA nodes  |
|               |        |        |specified      |                          |
+---------------+--------+--------+---------------+--------------------------+

CPUAllocation
"""""""""""""
This describes the granular CPU allocation requirements for VDUs.

:type:
    tosca.datatypes.compute.Container.Architecture.CPUAllocation

:properties:

+-----------------+-------+------------+-------------------------------------+
|Name             |Type   |Constraints |Description                          |
+-----------------+-------+------------+-------------------------------------+
|cpu_affinity     |String |One of      |Describes whether vCPU need to be    |
|                 |       |            |pinned to dedicated CPU core or      |
|                 |       |- shared    |shared dynamically                   |
|                 |       |- dedicated |                                     |
+-----------------+-------+------------+-------------------------------------+
|thread_allocation|String |One of      |Describes thread allocation          |
|                 |       |            |requirement                          |
|                 |       |- avoid     |                                     |
|                 |       |- separate  |                                     |
|                 |       |- isolate   |                                     |
|                 |       |- prefer    |                                     |
+-----------------+-------+------------+-------------------------------------+
|socket_count     |Integer| None       |Number of CPU sockets                |
+-----------------+-------+------------+-------------------------------------+
|core_count       |Integer| None       |Number of cores per socket           |
+-----------------+-------+------------+-------------------------------------+
|thread_count     |Integer| None       |Number of threads per core           |
+-----------------+-------+------------+-------------------------------------+

NUMA architecture
"""""""""""""""""
Following code snippet describes symmetric NUMA topology requirements for VDUs.

::

  ..
  VDU1:
    capabilities:
      mec_compute:
        properties:
          numa_node_count: 2
          numa_nodes: 3

For asymmetric NUMA architecture:

::

  ..
  VDU1:
    capabilities:
      mec_compute:
        properties:
          mem_size: 4096 MB
          num_cpus: 4
          numa_nodes:
            node0:
              id: 0
              vcpus: [0,1]
              mem_size: 1024 MB
            node1:
              id: 1
              vcpus: [2,3]
              mem_size: 3072 MB

:type:
    tosca.datatypes.compute.Container.Architecture.NUMA

:properties:

+--------+---------+-----------+-------------------------------------------+
|Name    |Type     |Constraints|Description                                |
+--------+---------+-----------+-------------------------------------------+
|id      |Integer  | >= 0      |CPU socket identifier                      |
+--------+---------+-----------+-------------------------------------------+
|vcpus   |Map of   |None       |List of specific host cpu numbers within a |
|        |integers |           |NUMA socket complex                        |
+--------+---------+-----------+-------------------------------------------+
|mem_size|scalar-  | >= 0MB    |Size of memory allocated from this NUMA    |
|        |unit.size|           |memory bank                                |
+--------+---------+-----------+-------------------------------------------+

Connection Points
-----------------
Connection point is used to connect the internal virtual link or outside
virtual link. It may be a virtual NIC or a SR-IOV NIC. Each connection
point has to bind to a VDU. A CP always requires a virtual link and a
virtual binding associated with it.

A code snippet for virtual NIC (Connection Point) without anti-spoof
protection and are accessible by the user. CP1 and CP2 are connected to
VDU1 in this order. Also CP1/CP2 are connected to VL1/VL2 respectively.

::

  ..
  topology_template:
    node_templates:
      VDU1:
        ..
      CP1:
        type: tosca.nodes.mec.CP.Apmec
        properties:
          mac_address: fa:40:08:a0:de:0a
          ip_address: 10.10.1.12
          type: vnic
          anti_spoofing_protection: false
          management: true
          order: 0
          security_groups:
            - secgroup1
            - secgroup2
        requirements:
          - virtualLink:
              node: VL1
          - virtualBinding:
              node: VDU1
      CP2:
        type: tosca.nodes.mec.CP.Apmec
        properties:
          type: vnic
          anti_spoofing_protection: false
          management: true
          order: 1
        requirements:
          - virtualLink:
              node: VL2
          - virtualBinding:
              node: VDU1
      VL1:
        ..
      VL2:
        ..

:type:
    tosca.nodes.mec.CP.Apmec

:properties:

+-------------------------+--------+-------+-----------+----------------------+
| Name                    |Required|Type   |Constraints| Description          |
+-------------------------+--------+-------+-----------+----------------------+
| type                    | No     |String |One of     | Specifies the type   |
|                         |        |       |           | of CP                |
|                         |        |       |- vnic     |                      |
|                         |        |       |  (default)|                      |
|                         |        |       |- sriov    |                      |
+-------------------------+--------+-------+-----------+----------------------+
| anti_spoofing_protection| No     |Boolean| None      | Indicates whether    |
|                         |        |       |           | anti_spoof rule is   |
|                         |        |       |           | enabled for the MEA  |
|                         |        |       |           | or not. Applicable   |
|                         |        |       |           | only when CP type is |
|                         |        |       |           | virtual NIC          |
+-------------------------+--------+-------+-----------+----------------------+
| management              | No     |Boolean| None      | Specifies whether the|
|                         |        |       |           | CP is accessible by  |
|                         |        |       |           | the user or not      |
+-------------------------+--------+-------+-----------+----------------------+
| order                   | No     |Integer| >= 0      | Uniquely numbered    |
|                         |        |       |           | order of CP within a |
|                         |        |       |           | VDU. Must be provided|
|                         |        |       |           | when binding more    |
|                         |        |       |           | than one CP to a VDU |
|                         |        |       |           | and ordering is      |
|                         |        |       |           | required.            |
+-------------------------+--------+-------+-----------+----------------------+
| security_groups         | No     |List   | None      | List of security     |
|                         |        |       |           | groups to be         |
|                         |        |       |           | associated with      |
|                         |        |       |           | the CP               |
+-------------------------+--------+-------+-----------+----------------------+
| mac_address             | No     |String | None      | The MAC address      |
+-------------------------+--------+-------+-----------+----------------------+
| ip _address             | No     |String | None      | The IP address       |
+-------------------------+--------+-------+-----------+----------------------+

:requirements:

+---------------+--------------------+-------------------+-------------------+
|Name           |Capability          |Relationship       |Description        |
+---------------+--------------------+-------------------+-------------------+
|virtualLink    |mec.VirtualLinkable |mec.VirtualLinksTo |States the VL node |
|               |                    |                   |to connect to      |
+---------------+--------------------+-------------------+-------------------+
|virtualbinding |mec.VirtualBindable |mec.VirtualBindsTo |States the VDU     |
|               |                    |                   |node to connect to |
+---------------+--------------------+-------------------+-------------------+

Virtual Links
-------------
Virtual link provides connectivity between VDUs. It represents the logical
virtual link entity.

An example of a virtual link whose vendor is Acme and is attached to network
net-01 is as shown below.

::

  ..
  topology_template:
    node_templates:
      VDU1:
        ..
      CP1:
        ..
      VL1:
        type: tosca.nodes.mec.VL
        properties:
          vendor: Acme
          network_name: net-01

:type:
    tosca.nodes.mec.VL

:properties:

+------------+----------+--------+-------------+-----------------------------+
|Name        | Required | Type   | Constraints | Description                 |
+------------+----------+--------+-------------+-----------------------------+
|vendor      | Yes      | String | None        | Vendor generating this VL   |
+------------+----------+--------+-------------+-----------------------------+
|network_name| Yes      | String | None        | Name of the network to which|
|            |          |        |             | VL is to be attached        |
+------------+----------+--------+-------------+-----------------------------+

Floating IP
-----------
Floating IP is used to access VDU from public network.

An example of assign floating ip to VDU

::

  ..
  topology_template:
    node_templates:
      VDU1:
        ..
      CP1:
        type: tosca.nodes.mec.CP.Apmec
        properties:
          management: true
        requirements:
          - virtualLink:
              node: VL1
          - virtualBinding:
              node: VDU1
      VL1:
        ..
      FIP1:
        type: tosca.nodes.network.FloatingIP
        properties:
          floating_network: public
        requirements:
          - link:
              node: CP1

:type:
    tosca.nodes.network.FloatingIP

:properties:

+-------------------+----------+--------+-------------+-----------------------+
|Name               | Required | Type   | Constraints | Description           |
+-------------------+----------+--------+-------------+-----------------------+
|floating_network   | Yes      | String | None        | Name of public network|
+-------------------+----------+--------+-------------+-----------------------+
|floating_ip_address| No       | String | None        | Floating IP Address   |
|                   |          |        |             | from public network   |
+------------+------+----------+--------+-------------+-----------------------+

:requirements:

+------+-------------------+--------------------+-------------------+
|Name  |Capability         |Relationship        |Description        |
+------+-------------------+--------------------+-------------------+
|link  |tosca.capabilities |tosca.relationships |States the CP node |
|      |.network.Linkable  |.network.LinksTo    |to connect to      |
+------+-------------------+--------------------+-------------------+

Multiple nodes
--------------
Multiple node types can be defined in a MEAD.

::

  ..
  topology_template:
    node_templates:
      VDU1:
        ..
      VDU2:
        ..
      CP1:
        ..
      CP2:
        ..
      VL1:
        ..
      VL2:
        ..

Summary
-------
To summarize MEAD is written in YAML and describes a MEA topology. It has
three node types, each with different capabilities and requirements. Below is
a template which mentions all node types with all available options.

::

     tosca_definitions_version: tosca_simple_profile_for_mec_1_0_0
     description: Sample MEAD template mentioning possible values for each node.
     metadata:
      template_name: sample-tosca-mead-template-guide
     topology_template:
      node_templates:
        VDU:
          type: tosca.nodes.mec.VDU.Apmec
          capabilities:
            mec_compute:
              properties:
                mem_page_size: [small, large, any, custom]
                cpu_allocation:
                  cpu_affinity: [shared, dedicated]
                  thread_allocation: [avoid, separate, isolate, prefer]
                  socket_count: any integer
                  core_count: any integer
                  thread_count: any integer
                numa_node_count: any integer
                numa_nodes:
                  node0: [ id: >=0, vcpus: [host CPU numbers], mem_size: >= 0MB]
          properties:
            image: Image to be used in VM
            flavor: Nova supported flavors
            availability_zone: available availability zone
            mem_size: in MB
            disk_size: in GB
            num_cpus: any integer
            metadata:
              entry_schema:
            config_drive: [true, false]
            monitoring_policy:
              name: [ping, noop, http-ping]
              parameters:
                monitoring_delay: delay time
                count: any integer
                interval: time to wait between monitoring
                timeout: monitoring timeout time
                actions:
                  [failure: respawn, failure: terminate, failure: log]
                retry: Number of retries
                port: specific port number if any
            config: Configuring the VDU as per the network function requirements
            mgmt_driver: [default=noop]
            service_type: type of network service to be done by VDU
            user_data: custom commands to be executed on VDU
            user_data_format: format of the commands
            key_name: user key
          artifacts:
            MEAImage:
              type: tosca.artifacts.Deployment.Image.VM
              file: file to be used for image
        CP:
          type: tosca.nodes.mec.CP.Apmec
          properties:
            management: [true, false]
            anti_spoofing_protection: [true, false]
            type: [ sriov, vnic ]
            order: order of CP within a VDU
            security_groups: list of security groups
          requirements:
            - virtualLink:
               node: VL to link to
            - virtualBinding:
               node: VDU to bind to
        VL:
          type: tosca.nodes.mec.VL
          properties:
            network_name: name of network to attach to
            vendor: Acme

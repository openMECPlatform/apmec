..
  Licensed under the Apache License, Version 2.0 (the "License"); you may
  not use this file except in compliance with the License. You may obtain
  a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
  License for the specific language governing permissions and limitations
  under the License.

.. _ref-mead:

=========================================
Orchestrating MEAs with attached Volumes
=========================================

To support persistent volumes to MEA, TOSCA MEC profile supports new type
of nodes. Apmec has now feature of parsing of those new nodes and creation
of cinder volumes  which are attached to the VDUs.


Prerequisites
~~~~~~~~~~~~~
To have persistent volume support to VDUs, we must enable cinder service in
addition to the other services that needed by Apmec.

MEAD Changes
~~~~~~~~~~~~

There are two steps to have volume attached to VDU:

* Create volume
* Attach Volume to VDU

Create Volume
~~~~~~~~~~~~~

To add volume, we need to add the below node to the MEAD:

.. code-block:: yaml

  VB1:
    type: tosca.nodes.BlockStorage.Apmec
    properties:
      size: 1 GB

Attach volume to VDU
~~~~~~~~~~~~~~~~~~~~
Next attach the created volume to VDU as below:

.. code-block:: yaml

  CB1:
    type: tosca.nodes.BlockStorageAttachment
    properties:
      location: /dev/vdb
      requirements:
        - virtualBinding:
            node: VDU1
        - virtualAttachment:
            node: VB1

With these additions, the new MEAD looks like below:

.. code-block:: yaml

  tosca_definitions_version: tosca_simple_profile_for_mec_1_0_0
  description: Demo example

  metadata:
    template_name: sample-tosca-mead

  topology_template:
    node_templates:
      VDU1:
        type: tosca.nodes.mec.VDU.Apmec
        capabilities:
          mec_compute:
            properties:
              num_cpus: 1
              mem_size: 512 MB
              disk_size: 1 GB
        properties:
          image: cirros-0.3.5-x86_64-disk
          availability_zone: nova
          mgmt_driver: noop
          config: |
            param0: key1
            param1: key2

      CP1:
        type: tosca.nodes.mec.CP.Apmec
        properties:
          management: true
          order: 0
          anti_spoofing_protection: false
        requirements:
          - virtualLink:
              node: VL1
          - virtualBinding:
              node: VDU1

      VB1:
        type: tosca.nodes.BlockStorage.Apmec
        properties:
          size: 1 GB

      CB1:
        type: tosca.nodes.BlockStorageAttachment
        properties:
          location: /dev/vdb
          requirements:
            - virtualBinding:
                node: VDU1
            - virtualAttachment:
                node: VB1

      VL1:
        type: tosca.nodes.mec.VL
        properties:
          network_name: net_mgmt
          vendor: Apmec

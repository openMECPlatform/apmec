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

.. _ref-multisite:

===================
Multisite VIM Usage
===================

A single Apmec controller node can be used to manage multiple Openstack sites
without having the need to deploy Apmec server on each of these sites. Apmec
allows users to deploy MEAs in multiple OpenStack sites using the multisite VIM
feature. OpenStack versions starting from Kilo are supported with this feature.


Preparing the OpenStack site
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create a new 'mec' project and admin privileged 'mec' user on the remote
   OpenStack site.
2. Create the required neutron networks for management, packet in and packet
   out networks that will be used by MEAs.

Register a new OpenStack VIM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To register a new OpenStack VIM inside Apmec.

::

 $ apmec vim-register --description 'OpenStack Liberty' --config-file vim_config.yaml Site1
 Created a new vim:
 +----------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
 | Field          | Value                                                                                                                                                    |
 +----------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
 | auth_cred      | {"username": "mec_user", "password": "***", "project_name": "mec", "user_id": "", "user_domain_name": "default", "auth_url":                               |
 |                | "http://10.18.161.165:5000/v3", "project_id": "", "project_domain_name": "default"}                                                                        |
 | auth_url       | http://10.18.161.165:5000/v3                                                                                                                             |
 | description    | OpenStack Liberty                                                                                                                                        |
 | id             | 3f3c51c5-8bda-4bd3-adb3-5ae62eae65c3                                                                                                                     |
 | name           | Site1                                                                                                                                                    |
 | placement_attr | {"regions": ["RegionOne", "RegionTwo"]}                                                                                                                  |
 | tenant_id      | 8907bae480c0414d98c3519acbad1b06                                                                                                                         |
 | type           | openstack                                                                                                                                                |
 | vim_project    | {"id": "", "name": "mec"}                                                                                                                                |
 +----------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+

In the above command, config.yaml contains VIM specific parameters as below:

::

 auth_url: 'http://localhost:5000'
 username: 'mec_user'
 password: 'devstack'
 project_name: 'mec'

The parameter auth_url points to the keystone service authorization URL of the
remote OpenStack site.

Default VIM configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

The default vim needs to be registered. This is required when the optional
argument -vim-id is not provided during mea-create. Refer to steps described in
`manual installation`_ to register default vim.

.. _manual installation: https://docs.openstack.org/apmec/latest/install/manual_installation.html#registering-default-vim

Deploying a new MEA on registered VIM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 $ apmec mea-create --description 'Openwrt MEA on Site1' --mead-id c3cbf0c0-a492-49e3-9541-945e49e7ed7e --vim-name Site1 openwrt_MEA
 Created a new mea:
 +----------------+--------------------------------------+
 | Field          | Value                                |
 +----------------+--------------------------------------+
 | description    | Openwrt tosca template               |
 | id             | 159ed8a5-a5a7-4f7a-be50-0f5f86603e3a |
 | instance_id    | 7b4ab046-d977-4781-9f0c-1ee9dcce01c6 |
 | mgmt_url       |                                      |
 | name           | openwrt_MEA                          |
 | placement_attr | {"vim_name": "Site1"}                |
 | status         | PENDING_CREATE                       |
 | tenant_id      | 8907bae480c0414d98c3519acbad1b06     |
 | vim_id         | 3f3c51c5-8bda-4bd3-adb3-5ae62eae65c3 |
 | mead_id        | c3cbf0c0-a492-49e3-9541-945e49e7ed7e |
 +----------------+--------------------------------------+

The --vim-id/--vim-name argument is optional during mea-create. If
--vim-id/--vim-name is not specified, the default vim will
be used to deploy MEA on the default site. We can create default vim
by specifying --is-default option with vim-register command.

User can optionally provide --vim-region-name during mea-create to deploy the
MEA in a specify region  within that VIM.

Updating a VIM
~~~~~~~~~~~~~~

Apmec allows for updating VIM authorization parameters such as 'username',
'password' and 'project_name' and 'ids' after it has been registered. To update
'username' and password' for a given VIM user within Apmec:

::

 $apmec vim-update VIM0 --config-file update.yaml

update.yaml in above command will contain:

::

 username: 'new_user'
 password: 'new_pw'

Note that 'auth_url' parameter of a VIM is not allowed to be updated as
'auth_url' uniquely identifies a given 'vim' resource.


Deleting a VIM
~~~~~~~~~~~~~~
To delete a VIM :

::

 $ apmec vim-delete VIM1
 Deleted vim: VIM1

Features
~~~~~~~~
* VIMs are shared across tenants -- As an admin operator, the user can register
  a VIM once and allow tenants to deploy MEAs on the registered VIM.
* Pluggable driver module framework allowing Apmec to interact with multiple
  VIM types.
* Compatible for OpenStack versions starting from Kilo.
* Supports keystone versions v2.0 and v3.

Limitations
~~~~~~~~~~~
* MEAs of all users currently land in the 'mec' project that is specified
  during VIM registration.
* Fernet keys for password encryption and decryption is stored on file systems.
  This is a limitation when multiple servers are serving behind a load balancer
  server and the keys need to be synced across apmec server systems.

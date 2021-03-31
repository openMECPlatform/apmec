# Copyright 2017 99cloud, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from apmec.extensions import mem
from apmec.tests.unit import base
from apmec.mem.infra_drivers.openstack import openstack


class TestOpenStack(base.TestCase):

    @mock.patch("apmec.mem.infra_drivers.openstack.heat_client.HeatClient")
    def test_create_wait_with_heat_connection_exception(self, mocked_hc):
        stack = {"stack_status", "CREATE_IN_PROGRESS"}
        mocked_hc.get.side_effect = [stack, Exception("any stuff")]
        openstack_driver = openstack.OpenStack()
        self.assertRaises(mem.MEACreateWaitFailed,
                          openstack_driver.create_wait,
                          None, None, {}, 'mea_id', None)

    @mock.patch("apmec.mem.infra_drivers.openstack.heat_client.HeatClient")
    def test_delete_wait_with_heat_connection_exception(self, mocked_hc):
        stack = {"stack_status", "DELETE_IN_PROGRESS"}
        mocked_hc.get.side_effect = [stack, Exception("any stuff")]
        openstack_driver = openstack.OpenStack()
        self.assertRaises(mem.MEADeleteWaitFailed,
                          openstack_driver.delete_wait,
                          None, None, 'mea_id', None, None)

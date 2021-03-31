# Copyright 2013, 2014 Intel Corporation.
# All Rights Reserved.
#
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
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

from oslo_log import log as logging

from apmec.mem.mgmt_drivers import abstract_driver


LOG = logging.getLogger(__name__)


class DeviceMgmtNoop(abstract_driver.DeviceMGMTAbstractDriver):
    def get_type(self):
        return 'noop'

    def get_name(self):
        return 'noop'

    def get_description(self):
        return 'Apmec MEAMgmt Noop Driver'

    def mgmt_url(self, plugin, context, mea):
        LOG.debug('mgmt_url %s', mea)
        return 'noop-mgmt-url'

    def mgmt_call(self, plugin, context, mea, kwargs):
        LOG.debug('mgmt_call %(mea)s %(kwargs)s',
                  {'mea': mea, 'kwargs': kwargs})

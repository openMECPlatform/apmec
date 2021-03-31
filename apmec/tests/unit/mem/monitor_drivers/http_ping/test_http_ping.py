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
#

import mock
import six.moves.urllib.error as urlerr
import testtools

from apmec.mem.monitor_drivers.http_ping import http_ping


class TestMEAMonitorHTTPPing(testtools.TestCase):

    def setUp(self):
        super(TestMEAMonitorHTTPPing, self).setUp()
        self.monitor_http_ping = http_ping.MEAMonitorHTTPPing()

    @mock.patch('six.moves.urllib.request.urlopen')
    def test_monitor_call_for_success(self, mock_urlopen):
        test_device = {}
        test_kwargs = {
            'mgmt_ip': 'a.b.c.d'
        }
        self.monitor_http_ping.monitor_call(test_device,
                                            test_kwargs)
        mock_urlopen.assert_called_once_with('http://a.b.c.d:80', timeout=5)

    @mock.patch('six.moves.urllib.request.urlopen')
    def test_monitor_call_for_failure(self, mock_urlopen):
        mock_urlopen.side_effect = urlerr.URLError("MOCK Error")
        test_device = {}
        test_kwargs = {
            'mgmt_ip': 'a.b.c.d'
        }
        monitor_return = self.monitor_http_ping.monitor_call(test_device,
                                                             test_kwargs)
        self.assertEqual('failure', monitor_return)

    def test_monitor_url(self):
        test_device = {
            'monitor_url': 'a.b.c.d'
        }
        test_monitor_url = self.monitor_http_ping.monitor_url(mock.ANY,
                                                              mock.ANY,
                                                              test_device)
        self.assertEqual('a.b.c.d', test_monitor_url)

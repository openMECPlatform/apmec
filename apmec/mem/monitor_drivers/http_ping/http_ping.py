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

from oslo_config import cfg
from oslo_log import log as logging
import six.moves.urllib.error as urlerr
import six.moves.urllib.request as urlreq

from apmec.common import log
from apmec.mem.monitor_drivers import abstract_driver


LOG = logging.getLogger(__name__)
OPTS = [
    cfg.IntOpt('retry', default=5,
               help=_('number of times to retry')),
    cfg.IntOpt('timeout', default=1,
               help=_('number of seconds to wait for a response')),
    cfg.IntOpt('port', default=80,
               help=_('HTTP port number to send request'))
]
cfg.CONF.register_opts(OPTS, 'monitor_http_ping')


def config_opts():
    return [('monitor_http_ping', OPTS)]


class MEAMonitorHTTPPing(abstract_driver.MEAMonitorAbstractDriver):
    def get_type(self):
        return 'http_ping'

    def get_name(self):
        return 'HTTP ping'

    def get_description(self):
        return 'Apmec HTTP Ping Driver for MEA'

    def monitor_url(self, plugin, context, mea):
        LOG.debug('monitor_url %s', mea)
        return mea.get('monitor_url', '')

    def _is_pingable(self, mgmt_ip='', retry=5, timeout=5, port=80, **kwargs):
        """Checks whether the server is reachable by using urllib.

        Waits for connectivity for `timeout` seconds,
        and if connection refused, it will retry `retry`
        times.
        :param mgmt_ip: IP to check
        :param retry: times to reconnect if connection refused
        :param timeout: seconds to wait for connection
        :param port: port number to check connectivity
        :return: bool - True or False depending on pingability.
        """
        url = 'http://' + mgmt_ip + ':' + str(port)
        for retry_index in range(int(retry)):
            try:
                urlreq.urlopen(url, timeout=timeout)
                return True
            except urlerr.URLError:
                LOG.warning('Unable to reach to the url %s', url)
        return 'failure'

    @log.log
    def monitor_call(self, mea, kwargs):
        if not kwargs['mgmt_ip']:
            return

        return self._is_pingable(**kwargs)

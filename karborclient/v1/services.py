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

from karborclient.common import base


class Service(base.Resource):
    def __repr__(self):
        return "<Service %s>" % self._info


class ServiceManager(base.ManagerWithFind):
    resource_class = Service

    def enable(self, service_id):
        """Enable the service specified by the service ID

        :param service_id: The ID of the service to enable.
        """
        body = {
            'status': 'enabled'
        }
        return self._update('/os-services/%s' % service_id, body, "service")

    def disable(self, service_id):
        """Disable the service specified by the service ID.

        :param service_id: The ID of the service to disable.
        """
        body = {
            'status': 'disabled'
        }
        return self._update('/os-services/%s' % service_id, body, "service")

    def disable_log_reason(self, service_id, reason):
        """Disable the service with a reason.

        :param service_id: The ID of the service to disable.
        :param reason: The reason for disabling a service.
        """
        body = {
            'status': 'disabled',
            'disabled_reason': reason
        }
        return self._update("/os-services/%s" % service_id, body, "service")

    def list(self, host=None, binary=None):
        """Lists all services."""
        search_opts = {
            'host': host,
            'binary': binary
        }
        resource_type = "os-services"
        url = self._build_list_url(resource_type, search_opts=search_opts)
        return self._list(url, 'services')

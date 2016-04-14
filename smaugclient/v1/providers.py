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

from smaugclient.common import base


class Provider(base.Resource):
    def __repr__(self):
        return "<Provider %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class ProviderManager(base.ManagerWithFind):
    resource_class = Provider

    def get(self, provider_id, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        url = "/providers/{provider_id}".format(
            provider_id=provider_id)
        return self._get(url, response_key="provider", headers=headers)

    def list(self, detailed=False, search_opts=None, marker=None, limit=None,
             sort_key=None, sort_dir=None, sort=None):
        """Lists all providers.

        :param detailed: Whether to return detailed provider info.
        :param search_opts: Search options to filter out provider.
        :param marker: Begin returning volumes that appear later in the
        provider  list than that represented by this provider id.
        :param limit: Maximum number of providers to return.
        :param sort_key: Key to be sorted; deprecated in kilo
        :param sort_dir: Sort direction, should be 'desc' or 'asc'; deprecated
                         in kilo
        :param sort: Sort information
        :rtype: list of :class:`Provider`
        """

        resource_type = "providers"
        url = self._build_list_url(
            resource_type, detailed=detailed,
            search_opts=search_opts, marker=marker,
            limit=limit, sort_key=sort_key,
            sort_dir=sort_dir, sort=sort)
        return self._list(url, 'providers')

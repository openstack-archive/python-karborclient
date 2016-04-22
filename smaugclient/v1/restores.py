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


class Restore(base.Resource):
    def __repr__(self):
        return "<Restore %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class RestoreManager(base.ManagerWithFind):
    resource_class = Restore

    def create(self, provider_id, checkpoint_id, restore_target, parameters):
        body = {'restore': {'provider_id': provider_id,
                            'checkpoint_id': checkpoint_id,
                            'restore_target': restore_target,
                            'parameters': parameters,
                            }
                }
        url = "/restores"
        return self._create(url, body, 'restore', return_raw=True)

    def delete(self, restore_id):
        path = '/restores/{restore_id}'.format(
            restore_id=restore_id)
        return self._delete(path)

    def get(self, restore_id, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        url = "/restores/{restore_id}".format(
            restore_id=restore_id)
        return self._get(url, response_key="restore", headers=headers)

    def list(self, detailed=False, search_opts=None, marker=None, limit=None,
             sort_key=None, sort_dir=None, sort=None):
        """Lists all restores.

        :param detailed: Whether to return detailed restore info.
        :param search_opts: Search options to filter out restores.
        :param marker: Begin returning volumes that appear later in the restore
                       list than that represented by this volume id.
        :param limit: Maximum number of restores to return.
        :param sort_key: Key to be sorted; deprecated in kilo
        :param sort_dir: Sort direction, should be 'desc' or 'asc'; deprecated
                         in kilo
        :param sort: Sort information
        :rtype: list of :class:`Restore`
        """

        resource_type = "restores"
        url = self._build_list_url(
            resource_type, detailed=detailed,
            search_opts=search_opts, marker=marker,
            limit=limit, sort_key=sort_key,
            sort_dir=sort_dir, sort=sort)
        return self._list(url, 'restores')

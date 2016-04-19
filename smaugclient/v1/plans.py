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


class Plan(base.Resource):
    def __repr__(self):
        return "<Plan %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class PlanManager(base.ManagerWithFind):
    resource_class = Plan

    def create(self, name, provider_id, resources, parameters):
        body = {'plan': {'name': name,
                         'provider_id': provider_id,
                         'resources': resources,
                         'parameters': parameters
                         }}
        url = "/plans"
        return self._create(url, body, 'plan', return_raw=True)

    def update(self, plan_id, data):

        body = {"plan": data}

        return self._update('/plans/{plan_id}'
                            .format(plan_id=plan_id),
                            body, "plan")

    def delete(self, plan_id):
        path = '/plans/{plan_id}'.format(
            plan_id=plan_id)
        return self._delete(path)

    def get(self, plan_id, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        url = "/plans/{plan_id}".format(
            plan_id=plan_id)
        return self._get(url, response_key="plan", headers=headers)

    def list(self, detailed=False, search_opts=None, marker=None, limit=None,
             sort_key=None, sort_dir=None, sort=None):
        """Lists all plans.

        :param detailed: Whether to return detailed volume info.
        :param search_opts: Search options to filter out volumes.
        :param marker: Begin returning volumes that appear later in the volume
                       list than that represented by this volume id.
        :param limit: Maximum number of volumes to return.
        :param sort_key: Key to be sorted; deprecated in kilo
        :param sort_dir: Sort direction, should be 'desc' or 'asc'; deprecated
                         in kilo
        :param sort: Sort information
        :rtype: list of :class:`Plan`
        """

        resource_type = "plans"
        url = self._build_list_url(
            resource_type, detailed=detailed,
            search_opts=search_opts, marker=marker,
            limit=limit, sort_key=sort_key,
            sort_dir=sort_dir, sort=sort)
        return self._list(url, 'plans')

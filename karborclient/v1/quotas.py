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


class Quota(base.Resource):
    def __repr__(self):
        return "<Quota %s>" % self._info


class QuotaManager(base.ManagerWithFind):
    resource_class = Quota

    def list(self):
        pass

    def update(self, project_id, data):

        if "plans" in data and data["plans"] is None:
            data["plans"] = 50

        body = {"quota": data}

        return self._update('/quotas/{project_id}'
                            .format(project_id=project_id),
                            body, "quota")

    def get(self, project_id, detail, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        base_url = "/quotas/{project_id}".format(
            project_id=project_id)
        if detail:
            url = base_url + '/detail'
        else:
            url = base_url
        return self._get(url, response_key="quota", headers=headers)

    def defaults(self, project_id, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        url = "/quotas/{project_id}/defaults".format(
            project_id=project_id)
        return self._get(url, response_key="quota", headers=headers)

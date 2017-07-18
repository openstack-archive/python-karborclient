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


class OperationLog(base.Resource):
    def __repr__(self):
        return "<OperationLog %s>" % self._info


class OperationLogManager(base.ManagerWithFind):
    resource_class = OperationLog

    def get(self, operation_log_id, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        url = "/operation_logs/{operation_log_id}".format(
            operation_log_id=operation_log_id)
        return self._get(url, response_key="operation_log", headers=headers)

    def list(self, detailed=False, search_opts=None, marker=None, limit=None,
             sort_key=None, sort_dir=None, sort=None):
        """Lists all operation_logs.

        """
        resource_type = "operation_logs"
        url = self._build_list_url(
            resource_type, detailed=detailed,
            search_opts=search_opts, marker=marker,
            limit=limit, sort_key=sort_key,
            sort_dir=sort_dir, sort=sort)
        return self._list(url, 'operation_logs')

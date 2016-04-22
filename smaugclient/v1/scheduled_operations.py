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


class ScheduledOperation(base.Resource):
    def __repr__(self):
        return "<ScheduledOperation %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class ScheduledOperationManager(base.ManagerWithFind):
    resource_class = ScheduledOperation

    def create(self, name, operation_type, trigger_id, operation_definition):
        body = {'scheduled_operation': {'name': name,
                                        'operation_type': operation_type,
                                        'trigger_id': trigger_id,
                                        'operation_definition':
                                            operation_definition,
                                        }}
        url = "/scheduled_operations"
        return self._create(url, body, 'scheduled_operation', return_raw=True)

    def delete(self, scheduled_operation_id):
        path = '/scheduled_operations/{scheduled_operation_id}'.\
            format(scheduled_operation_id=scheduled_operation_id)
        return self._delete(path)

    def get(self, scheduled_operation_id, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        url = "/scheduled_operations/{scheduled_operation_id}".\
            format(scheduled_operation_id=scheduled_operation_id)
        return self._get(url, response_key="scheduled_operation",
                         headers=headers)

    def list(self, detailed=False, search_opts=None, marker=None, limit=None,
             sort_key=None, sort_dir=None, sort=None):
        """Lists all scheduled_operations."""

        resource_type = "scheduled_operations"
        url = self._build_list_url(
            resource_type, detailed=detailed,
            search_opts=search_opts, marker=marker,
            limit=limit, sort_key=sort_key,
            sort_dir=sort_dir, sort=sort)
        return self._list(url, 'operations')

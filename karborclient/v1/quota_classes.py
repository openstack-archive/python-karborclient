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


class QuotaClass(base.Resource):
    def __repr__(self):
        return "<QuotaClass %s>" % self._info


class QuotaClassManager(base.ManagerWithFind):
    resource_class = QuotaClass

    def list(self):
        pass

    def update(self, class_name, data):

        if "plans" in data and data["plans"] is None:
            data["plans"] = 50

        body = {"quota_class": data}

        return self._update('/quota_classes/{class_name}'
                            .format(class_name=class_name),
                            body, "quota_class")

    def get(self, class_name, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        url = "/quota_classes/{class_name}".format(
            class_name=class_name)
        return self._get(url, response_key="quota_class", headers=headers)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy

from karborclient.osc.v1 import protectables as osc_protectables
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import protectables


PROTECTABLE_LIST_INFO = {
    "protectable_type": [
        "OS::Keystone::Project",
        "OS::Cinder::Volume",
        "OS::Glance::Image",
        "OS::Nova::Server"
    ]
}

PROTECTABLE_SHOW_INFO = {
    "name": "OS::Nova::Server",
    "dependent_types": [
        "OS::Cinder::Volume",
        "OS::Glance::Image"
    ]
}

PROTECTABLE_INSTANCE_LIST_INFO = {
    "id": "25336116-f38e-4c22-81ad-e9b7bd71ba51",
    "type": "OS::Cinder::Volume",
    "name": "System volume",
    "extra_info": {
        "availability_zone": "az1"
    }
}

PROTECTABLE_INSTANCE_SHOW_INFO = {
    "id": "cb4ef2ff-10f5-46c9-bce4-cf7a49c65a01",
    "type": "OS::Nova::Server",
    "name": "My VM",
    "dependent_resources": [{
        "id": "99777fdd-8a5b-45ab-ba2c-52420008103f",
        "type": "OS::Glance::Image",
        "name": "cirros-0.3.4-x86_64-uec"}]
}


class TestProtectables(fakes.TestDataProtection):
    def setUp(self):
        super(TestProtectables, self).setUp()
        cm = self.app.client_manager
        self.protectables_mock = cm.data_protection.protectables
        self.protectables_mock.reset_mock()


class TestListProtectables(TestProtectables):
    def setUp(self):
        super(TestListProtectables, self).setUp()
        self.protectables_mock.list.return_value = [protectables.Protectable(
            None, copy.deepcopy(PROTECTABLE_LIST_INFO))]

        # Command to test
        self.cmd = osc_protectables.ListProtectables(self.app, None)

    def test_protectables_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            ['Protectable type'])
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [(['OS::Keystone::Project',
                           'OS::Cinder::Volume',
                           'OS::Glance::Image',
                           'OS::Nova::Server'],)]
        self.assertEqual(expected_data, list(data))


class TestShowProtectable(TestProtectables):
    def setUp(self):
        super(TestShowProtectable, self).setUp()
        self.protectables_mock.get.return_value = protectables.Protectable(
            None, copy.deepcopy(PROTECTABLE_SHOW_INFO))
        # Command to test
        self.cmd = osc_protectables.ShowProtectable(self.app, None)

    def test_protectable_show(self):
        arglist = ['OS::Nova::Server']
        verifylist = [('protectable_type', 'OS::Nova::Server')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.protectables_mock.get.assert_called_once_with(
            'OS::Nova::Server')


class TestListProtectableInstances(TestProtectables):
    def setUp(self):
        super(TestListProtectableInstances, self).setUp()
        pm = self.protectables_mock
        pm.list_instances.return_value = [protectables.Instances(
            None, copy.deepcopy(PROTECTABLE_INSTANCE_LIST_INFO)), ]
        # Command to test
        self.cmd = osc_protectables.ListProtectableInstances(self.app, None)

    def test_protectable_instances_list(self):
        arglist = ['OS::Cinder::Volume']
        verifylist = [('protectable_type', 'OS::Cinder::Volume')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.protectables_mock.list_instances.assert_called_once_with(
            'OS::Cinder::Volume', limit=None, marker=None,
            search_opts={'type': None, 'parameters': None},
            sort=None)


class TestShowProtectableInstance(TestProtectables):
    def setUp(self):
        super(TestShowProtectableInstance, self).setUp()
        pm = self.protectables_mock
        pm.get_instance.return_value = protectables.Instances(
            None, copy.deepcopy(PROTECTABLE_INSTANCE_SHOW_INFO))
        # Command to test
        self.cmd = osc_protectables.ShowProtectableInstance(self.app, None)

    def test_protectable_instance_show(self):
        arglist = ['OS::Nova::Server', 'cb4ef2ff-10f5-46c9-bce4-cf7a49c65a01']
        verifylist = [('protectable_type', 'OS::Nova::Server'),
                      ('protectable_id',
                       'cb4ef2ff-10f5-46c9-bce4-cf7a49c65a01')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.protectables_mock.get_instance.assert_called_once_with(
            'OS::Nova::Server', 'cb4ef2ff-10f5-46c9-bce4-cf7a49c65a01',
            search_opts={'parameters': None})

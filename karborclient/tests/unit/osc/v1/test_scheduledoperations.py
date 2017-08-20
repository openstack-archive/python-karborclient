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
import json

from karborclient.osc.v1 import scheduled_operations as osc_so
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import scheduled_operations


SCHEDULEDOPERATION_INFO = {
    "id": "1a2c0c3d-f402-4cd8-b5db-82e85cb51fad",
    "name": "My scheduled operation",
    "description": "It will run everyday",
    "operation_type": "protect",
    "trigger_id": "23902b02-5666-4ee6-8dfe-962ac09c3995",
    "operation_definition": {
        "provider_id": "2a9ce1f3-cc1a-4516-9435-0ebb13caa399",
        "plan_id": "2a9ce1f3-cc1a-4516-9435-0ebb13caa398"
    },
    "enabled": 1
}


class TestScheduledOperations(fakes.TestDataProtection):
    def setUp(self):
        super(TestScheduledOperations, self).setUp()
        self.so_mock = self.app.client_manager.data_protection.\
            scheduled_operations
        self.so_mock.reset_mock()


class TestListScheduledOperations(TestScheduledOperations):
    def setUp(self):
        super(TestListScheduledOperations, self).setUp()
        self.so_mock.list.return_value = [
            scheduled_operations.ScheduledOperation(
                None, copy.deepcopy(SCHEDULEDOPERATION_INFO))
        ]

        # Command to test
        self.cmd = osc_so.ListScheduledOperations(self.app, None)

    def test_scheduled_operations_list(self):
        arglist = ['--name', 'My scheduled operation']
        verifylist = [('name', 'My scheduled operation')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            ['Id', 'Name', 'Operation Type', 'Trigger Id',
             'Operation Definition'])
        self.assertEqual(expected_columns, columns)

        operation_definition = {
            "provider_id": "2a9ce1f3-cc1a-4516-9435-0ebb13caa399",
            "plan_id": "2a9ce1f3-cc1a-4516-9435-0ebb13caa398"
        }

        # Check that data is correct
        expected_data = [("1a2c0c3d-f402-4cd8-b5db-82e85cb51fad",
                          "My scheduled operation",
                          "protect",
                          "23902b02-5666-4ee6-8dfe-962ac09c3995",
                          json.dumps(operation_definition,
                                     indent=2, sort_keys=True)
                          )]
        self.assertEqual(expected_data, data)


class TestCreateScheduledOperation(TestScheduledOperations):
    def setUp(self):
        super(TestCreateScheduledOperation, self).setUp()
        self.so_mock.create.return_value = scheduled_operations.\
            ScheduledOperation(None, copy.deepcopy(SCHEDULEDOPERATION_INFO))
        # Command to test
        self.cmd = osc_so.CreateScheduledOperation(self.app, None)

    def test_scheduled_operation_create(self):
        arglist = ['My scheduled operation',
                   'protect',
                   "23902b02-5666-4ee6-8dfe-962ac09c3995",
                   "'provider_id=2a9ce1f3-cc1a-4516-9435-0ebb13caa399,"
                   "plan_id=2a9ce1f3-cc1a-4516-9435-0ebb13caa398'"]
        verifylist = [('name', 'My scheduled operation'),
                      ('operation_type', 'protect'),
                      ('trigger_id', "23902b02-5666-4ee6-8dfe-962ac09c3995"),
                      ('operation_definition',
                       "'provider_id=2a9ce1f3-cc1a-4516-9435-0ebb13caa399,"
                       "plan_id=2a9ce1f3-cc1a-4516-9435-0ebb13caa398'")]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.so_mock.create.assert_called_once_with(
            'My scheduled operation',
            'protect',
            '23902b02-5666-4ee6-8dfe-962ac09c3995',
            "'provider_id=2a9ce1f3-cc1a-4516-9435-0ebb13caa399,"
            "plan_id=2a9ce1f3-cc1a-4516-9435-0ebb13caa398'")


class TestDeleteScheduledOperation(TestScheduledOperations):
    def setUp(self):
        super(TestDeleteScheduledOperation, self).setUp()
        self.so_mock.get.return_value = scheduled_operations.\
            ScheduledOperation(None, copy.deepcopy(SCHEDULEDOPERATION_INFO))
        # Command to test
        self.cmd = osc_so.DeleteScheduledOperation(self.app, None)

    def test_scheduled_operation_delete(self):
        arglist = ['1a2c0c3d-f402-4cd8-b5db-82e85cb51fad']
        verifylist = [('scheduledoperation',
                       ['1a2c0c3d-f402-4cd8-b5db-82e85cb51fad'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.so_mock.delete.assert_called_once_with(
            '1a2c0c3d-f402-4cd8-b5db-82e85cb51fad')


class TestShowScheduledOperation(TestScheduledOperations):
    def setUp(self):
        super(TestShowScheduledOperation, self).setUp()
        self._schedop_info = copy.deepcopy(SCHEDULEDOPERATION_INFO)
        self.so_mock.get.return_value = scheduled_operations.\
            ScheduledOperation(None, self._schedop_info)

        # Command to test
        self.cmd = osc_so.ShowScheduledOperation(self.app, None)

    def test_scheduled_operation_show(self):
        arglist = ['1a2c0c3d-f402-4cd8-b5db-82e85cb51fad']
        verifylist = [('scheduledoperation',
                       '1a2c0c3d-f402-4cd8-b5db-82e85cb51fad')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            'description', 'enabled', 'id', 'name', 'operation_definition',
            'operation_type', 'trigger_id')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        self.assertEqual(self._schedop_info['description'], data[0])
        self.assertEqual(self._schedop_info['enabled'], data[1])
        self.assertEqual(self._schedop_info['id'], data[2])
        self.assertEqual(self._schedop_info['name'], data[3])
        self.assertEqual(self._schedop_info['operation_definition'], data[4])
        self.assertEqual(self._schedop_info['operation_type'], data[5])
        self.assertEqual(self._schedop_info['trigger_id'], data[6])

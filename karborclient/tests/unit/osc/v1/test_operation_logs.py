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

from karborclient.osc.v1 import operation_logs as osc_operation_logs
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import operation_logs


OPERATIONLOG_INFO = {
    "id": "22b82aa7-9179-4c71-bba2-caf5c0e68db7",
    "project_id": "e486a2f49695423ca9c47e589b948108",
    "operation_type": "protect",
    "checkpoint_id": "dcb20606-ad71-40a3-80e4-ef0fafdad0c3",
    "plan_id": "cf56bd3e-97a7-4078-b6d5-f36246333fd9",
    "provider_id": "23902b02-5666-4ee6-8dfe-962ac09c3994",
    "restore_id": None,
    "scheduled_operation_id": "23902b02-5666-4ee6-8dfe-962ac09c3991",
    "started_at": "2015-08-27T09:50:58-05:00",
    "ended_at": "2015-08-27T10:50:58-05:00",
    "status": "protecting",
    "error_info": "Could not access bank",
    "extra_info": None
}


class TestOperationLogs(fakes.TestDataProtection):
    def setUp(self):
        super(TestOperationLogs, self).setUp()
        self.operation_logs_mock = (
            self.app.client_manager.data_protection.operation_logs)
        self.operation_logs_mock.reset_mock()


class TestListOperationLogs(TestOperationLogs):
    def setUp(self):
        super(TestListOperationLogs, self).setUp()
        self.operation_logs_mock.list.return_value = [
            operation_logs.OperationLog(None,
                                        copy.deepcopy(OPERATIONLOG_INFO))]

        # Command to test
        self.cmd = osc_operation_logs.ListOperationLogs(self.app, None)

    def test_operation_logs_list(self):
        arglist = ['--status', 'success']
        verifylist = [('status', 'success')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            ['Id', 'Operation Type', 'Checkpoint id', 'Plan Id',
             'Provider id', 'Restore Id', 'Scheduled Operation Id',
             'Status', 'Started At', 'Ended At', 'Error Info',
             'Extra Info'])
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [("22b82aa7-9179-4c71-bba2-caf5c0e68db7",
                          "protect",
                          "dcb20606-ad71-40a3-80e4-ef0fafdad0c3",
                          "cf56bd3e-97a7-4078-b6d5-f36246333fd9",
                          "23902b02-5666-4ee6-8dfe-962ac09c3994",
                          None,
                          "23902b02-5666-4ee6-8dfe-962ac09c3991",
                          "protecting",
                          "2015-08-27T09:50:58-05:00",
                          "2015-08-27T10:50:58-05:00",
                          "Could not access bank",
                          None)]
        self.assertEqual(expected_data, list(data))


class TestShowOperationLog(TestOperationLogs):
    def setUp(self):
        super(TestShowOperationLog, self).setUp()
        self._oplog_info = copy.deepcopy(OPERATIONLOG_INFO)
        self.operation_logs_mock.get.return_value = (
            operation_logs.OperationLog(None, self._oplog_info))

        # Command to test
        self.cmd = osc_operation_logs.ShowOperationLog(self.app, None)

    def test_operation_log_show(self):
        arglist = ['22b82aa7-9179-4c71-bba2-caf5c0e68db7']
        verifylist = [('operation_log',
                       '22b82aa7-9179-4c71-bba2-caf5c0e68db7')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            'checkpoint_id', 'ended_at', 'error_info', 'extra_info',
            'id', 'operation_type', 'plan_id', 'project_id',
            'provider_id', 'restore_id', 'scheduled_operation_id',
            'started_at', 'status')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        self.assertEqual(self._oplog_info['checkpoint_id'], data[0])
        self.assertEqual(self._oplog_info['ended_at'], data[1])
        self.assertEqual(self._oplog_info['error_info'], data[2])
        self.assertEqual(self._oplog_info['extra_info'], data[3])
        self.assertEqual(self._oplog_info['id'], data[4])
        self.assertEqual(self._oplog_info['operation_type'], data[5])
        self.assertEqual(self._oplog_info['plan_id'], data[6])
        self.assertEqual(self._oplog_info['project_id'], data[7])
        self.assertEqual(self._oplog_info['provider_id'], data[8])
        self.assertEqual(self._oplog_info['restore_id'], data[9])
        self.assertEqual(self._oplog_info['scheduled_operation_id'], data[10])
        self.assertEqual(self._oplog_info['started_at'], data[11])
        self.assertEqual(self._oplog_info['status'], data[12])

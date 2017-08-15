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

from karborclient.osc.v1 import triggers as osc_triggers
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import triggers


TRIGGER_INFO = {
    "id": "2a9ce1f3-cc1a-4516-9435-0ebb13caa398",
    "name": "My backup trigger",
    "type": "time",
    "properties": {
        "format": "calendar",
        "pattern": "BEGIN:VEVENT\\nRRULE:FREQ=HOURLY;INTERVAL=1;\\nEND:VEVENT",
        "start_time": "2015-12-17T08:30:00",
        "end_time": "2016-03-17T08:30:00",
        "window": "3600"
    }
}


class TestTriggers(fakes.TestDataProtection):
    def setUp(self):
        super(TestTriggers, self).setUp()
        self.triggers_mock = self.app.client_manager.data_protection.triggers
        self.triggers_mock.reset_mock()


class TestListTriggers(TestTriggers):
    def setUp(self):
        super(TestListTriggers, self).setUp()
        self.triggers_mock.list.return_value = [triggers.Trigger(
            None, copy.deepcopy(TRIGGER_INFO))]

        # Command to test
        self.cmd = osc_triggers.ListTriggers(self.app, None)

    def test_triggers_list(self):
        arglist = ['--name', 'My backup trigger']
        verifylist = [('name', 'My backup trigger')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            ['Id', 'Name', 'Type', 'Properties'])
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [("2a9ce1f3-cc1a-4516-9435-0ebb13caa398",
                          "My backup trigger",
                          "time",
                          {"format": "calendar",
                           "pattern": "BEGIN:VEVENT\\nRRULE:FREQ=HOURLY;INTERVAL=1;\\nEND:VEVENT",  # noqa
                           "start_time": "2015-12-17T08:30:00",
                           "end_time": "2016-03-17T08:30:00",
                           "window": "3600"})]
        self.assertEqual(expected_data, list(data))


class TestCreateTrigger(TestTriggers):
    def setUp(self):
        super(TestCreateTrigger, self).setUp()
        self.triggers_mock.create.return_value = triggers.Trigger(
            None, copy.deepcopy(TRIGGER_INFO))
        # Command to test
        self.cmd = osc_triggers.CreateTrigger(self.app, None)

    def test_trigger_create(self):
        arglist = ['My backup trigger',
                   'time',
                   "'format'='calendar',"
                   "'pattern'='BEGIN:VEVENT\\nRRULE:FREQ=HOURLY;INTERVAL=1;\\nEND:VEVENT',"  # noqa
                   "'start_time'='2015-12-17T08:30:00',"
                   "'end_time'='2016-03-17T08:30:00',"
                   "'window'='3600'"]
        verifylist = [('name', 'My backup trigger'),
                      ('type', 'time'),
                      ('properties', "'format'='calendar',"
                                     "'pattern'='BEGIN:VEVENT\\nRRULE:FREQ=HOURLY;INTERVAL=1;\\nEND:VEVENT',"  # noqa
                                     "'start_time'='2015-12-17T08:30:00',"
                                     "'end_time'='2016-03-17T08:30:00',"
                                     "'window'='3600'")]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.triggers_mock.create.assert_called_once_with(
            'My backup trigger',
            'time',
            "'format'='calendar',"
            "'pattern'='BEGIN:VEVENT\\nRRULE:FREQ=HOURLY;INTERVAL=1;\\nEND:VEVENT',"  # noqa
            "'start_time'='2015-12-17T08:30:00',"
            "'end_time'='2016-03-17T08:30:00',"
            "'window'='3600'")


class TestUpdateTrigger(TestTriggers):
    def setUp(self):
        super(TestUpdateTrigger, self).setUp()
        self.triggers_mock.get.return_value = triggers.Trigger(
            None, copy.deepcopy(TRIGGER_INFO))
        self.triggers_mock.update.return_value = triggers.Trigger(
            None, copy.deepcopy(TRIGGER_INFO))
        # Command to test
        self.cmd = osc_triggers.UpdateTrigger(self.app, None)

    def test_trigger_update(self):
        arglist = ['2a9ce1f3-cc1a-4516-9435-0ebb13caa398',
                   '--name', 'My backup trigger']
        verifylist = [('trigger_id', '2a9ce1f3-cc1a-4516-9435-0ebb13caa398'),
                      ('name', 'My backup trigger')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.triggers_mock.update.assert_called_once_with(
            '2a9ce1f3-cc1a-4516-9435-0ebb13caa398',
            {'name': 'My backup trigger'})


class TestDeleteTrigger(TestTriggers):
    def setUp(self):
        super(TestDeleteTrigger, self).setUp()
        self.triggers_mock.get.return_value = triggers.Trigger(
            None, copy.deepcopy(TRIGGER_INFO))
        # Command to test
        self.cmd = osc_triggers.DeleteTrigger(self.app, None)

    def test_trigger_delete(self):
        arglist = ['2a9ce1f3-cc1a-4516-9435-0ebb13caa398']
        verifylist = [('trigger', ['2a9ce1f3-cc1a-4516-9435-0ebb13caa398'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.triggers_mock.delete.assert_called_once_with(
            '2a9ce1f3-cc1a-4516-9435-0ebb13caa398')


class TestShowTrigger(TestTriggers):
    def setUp(self):
        super(TestShowTrigger, self).setUp()
        self._trigger_info = copy.deepcopy(TRIGGER_INFO)
        self.triggers_mock.get.return_value = triggers.Trigger(
            None, self._trigger_info)

        # Command to test
        self.cmd = osc_triggers.ShowTrigger(self.app, None)

    def test_trigger_show(self):
        arglist = ['2a9ce1f3-cc1a-4516-9435-0ebb13caa398']
        verifylist = [('trigger', '2a9ce1f3-cc1a-4516-9435-0ebb13caa398')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            'id', 'name', 'properties', 'type')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        self.assertEqual(self._trigger_info['id'], data[0])
        self.assertEqual(self._trigger_info['name'], data[1])
        self.assertEqual(self._trigger_info['properties'], data[2])
        self.assertEqual(self._trigger_info['type'], data[3])

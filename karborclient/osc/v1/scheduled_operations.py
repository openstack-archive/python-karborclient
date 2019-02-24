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

"""Data protection V1 scheduled_operations action implementations"""

import functools
import six

from oslo_serialization import jsonutils
from oslo_utils import uuidutils

from osc_lib.command import command
from osc_lib import utils as osc_utils
from oslo_log import log as logging

from karborclient.common.apiclient import exceptions
from karborclient.i18n import _


def format_scheduledoperation(scheduledoperation_info):
    for key in ('operation_definition', ):
        if key not in scheduledoperation_info:
            continue
        scheduledoperation_info[key] = jsonutils.dumps(
            scheduledoperation_info[key], indent=2, sort_keys=True)
    scheduledoperation_info.pop("links", None)


class ListScheduledOperations(command.Lister):
    _description = _("List scheduled_operations.")

    log = logging.getLogger(__name__ + ".ListScheduledOperations")

    def get_parser(self, prog_name):
        parser = super(ListScheduledOperations, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Shows details for all tenants. Admin only.'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Filters results by a name. Default=None.'),
        )
        parser.add_argument(
            '--operation_type',
            metavar='<operation_type>',
            default=None,
            help=_('Filters results by a type. Default=None.'),
        )
        parser.add_argument(
            '--trigger_id',
            metavar='<trigger_id>',
            default=None,
            help=_('Filters results by a trigger id. Default=None.'),
        )
        parser.add_argument(
            '--operation_definition',
            metavar='<operation_definition>',
            default=None,
            help=_('Filters results by a operation definition. Default=None.'),
        )
        parser.add_argument(
            '--marker',
            metavar='<scheduled_operations>',
            help=_('The last scheduled_operations ID of the previous page'),
        )
        parser.add_argument(
            '--limit',
            type=int,
            metavar='<num-scheduled_operations>',
            help=_('Maximum number of scheduled_operations to display'),
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            default=None,
            help=_("Sort output by selected keys and directions(asc or desc) "
                   "(default: name:asc), multiple keys and directions can be "
                   "specified separated by comma"),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Filter results by a project(admin only)')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        data_protection_client = self.app.client_manager.data_protection
        all_projects = bool(parsed_args.project) or parsed_args.all_projects

        search_opts = {
            'all_tenants': all_projects,
            'project_id': parsed_args.project,
            'name': parsed_args.name,
            'operation_type': parsed_args.operation_type,
            'trigger_id': parsed_args.trigger_id,
            'operation_definition': parsed_args.operation_definition,
        }

        data = data_protection_client.scheduled_operations.list(
            search_opts=search_opts, marker=parsed_args.marker,
            limit=parsed_args.limit, sort=parsed_args.sort)

        column_headers = ['Id', 'Name', 'Operation Type', 'Trigger Id',
                          'Operation Definition']

        json_dumps = functools.partial(jsonutils.dumps,
                                       indent=2,
                                       sort_keys=True)
        formatters = {
            "Operation Definition": json_dumps,
        }
        return (column_headers,
                list(osc_utils.get_item_properties(
                    s, column_headers, formatters=formatters,
                ) for s in data))


class ShowScheduledOperation(command.ShowOne):
    _description = "Shows scheduled_operation details"

    def get_parser(self, prog_name):
        parser = super(ShowScheduledOperation, self).get_parser(prog_name)
        parser.add_argument(
            'scheduledoperation',
            metavar="<scheduledoperation>",
            help=_('The UUID of the scheduledoperation.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        so = osc_utils.find_resource(client.scheduled_operations,
                                     parsed_args.scheduledoperation)

        format_scheduledoperation(so._info)
        return zip(*sorted(six.iteritems(so._info)))


class CreateScheduledOperation(command.ShowOne):
    _description = "Creates a scheduled operation"

    def get_parser(self, prog_name):
        parser = super(CreateScheduledOperation, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('The name of the scheduled operation.')
        )
        parser.add_argument(
            'operation_type',
            metavar='<operation_type>',
            help=_('Operation Type of scheduled operation.')
        )
        parser.add_argument(
            'trigger_id',
            metavar='<trigger_id>',
            help=_('Trigger id of scheduled operation.')
        )
        parser.add_argument(
            'operation_definition',
            metavar='<key=value,key=value>',
            help=_('Operation definition of scheduled operation.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        if not uuidutils.is_uuid_like(parsed_args.trigger_id):
            raise exceptions.CommandError(
                "Invalid trigger id provided.")
        so = client.scheduled_operations.create(
            parsed_args.name, parsed_args.operation_type,
            parsed_args.trigger_id, parsed_args.operation_definition)

        format_scheduledoperation(so._info)
        return zip(*sorted(six.iteritems(so._info)))


class DeleteScheduledOperation(command.Command):
    _description = "Delete scheduled operation"

    def get_parser(self, prog_name):
        parser = super(DeleteScheduledOperation, self).get_parser(prog_name)
        parser.add_argument(
            'scheduledoperation',
            metavar='<scheduledoperation>',
            nargs="+",
            help=_('ID of scheduled operation.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        failure_count = 0
        for so_id in parsed_args.scheduledoperation:
            try:
                so = osc_utils.find_resource(client.scheduled_operations,
                                             so_id)
                client.scheduled_operations.delete(so.id)
            except exceptions.NotFound:
                failure_count += 1
                print("Failed to delete '%s'; scheduled operation "
                      "not found" % so_id)
        if failure_count == len(parsed_args.scheduledoperation):
            raise exceptions.CommandError(
                "Unable to find and delete any of the "
                "specified scheduled operation.")

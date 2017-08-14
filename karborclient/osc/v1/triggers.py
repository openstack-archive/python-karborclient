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

"""Data protection V1 triggers action implementations"""

from osc_lib.command import command
from osc_lib import utils as osc_utils
from oslo_log import log as logging

from karborclient.common.apiclient import exceptions
from karborclient.i18n import _
from karborclient import utils


class ListTriggers(command.Lister):
    _description = _("List triggers.")

    log = logging.getLogger(__name__ + ".ListTriggers")

    def get_parser(self, prog_name):
        parser = super(ListTriggers, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Shows details for all tenants. Admin only.'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            default=None,
            help=_('Filters results by a name. Default=None.'),
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            default=None,
            help=_('Filters results by a type. Default=None.'),
        )
        parser.add_argument(
            '--properties',
            metavar='<properties>',
            default=None,
            help=_('Filters results by a properties. Default=None.'),
        )
        parser.add_argument(
            '--marker',
            metavar='<trigger>',
            help=_('The last trigger ID of the previous page'),
        )
        parser.add_argument(
            '--limit',
            type=int,
            metavar='<num-triggers>',
            help=_('Maximum number of triggers to display'),
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
            help=_('Display information from single tenant (Admin only).')
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
            'type': parsed_args.type,
            'properties': parsed_args.properties,
        }

        data = data_protection_client.triggers.list(
            search_opts=search_opts, marker=parsed_args.marker,
            limit=parsed_args.limit, sort=parsed_args.sort)

        column_headers = ['Id', 'Name', 'Type', 'Properties']

        return (column_headers,
                (osc_utils.get_item_properties(
                    s, column_headers
                ) for s in data))


class ShowTrigger(command.ShowOne):
    _description = "Shows trigger details"

    def get_parser(self, prog_name):
        parser = super(ShowTrigger, self).get_parser(prog_name)
        parser.add_argument(
            'trigger',
            metavar="<trigger>",
            help=_('The UUID of the trigger.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        trigger = osc_utils.find_resource(client.triggers, parsed_args.trigger)

        trigger._info.pop("links", None)
        return zip(*sorted(trigger._info.items()))


class CreateTrigger(command.ShowOne):
    _description = "Creates a trigger"

    def get_parser(self, prog_name):
        parser = super(CreateTrigger, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('The name of the trigger.')
        )
        parser.add_argument(
            'type',
            metavar='<type>',
            help=_('Type of trigger.')
        )
        parser.add_argument(
            'properties',
            metavar='<key=value,key=value>',
            help=_('Properties of trigger.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        trigger = client.triggers.create(parsed_args.name, parsed_args.type,
                                         parsed_args.properties)

        trigger._info.pop("links", None)
        return zip(*sorted(trigger._info.items()))


class UpdateTrigger(command.ShowOne):
    _description = "Update a trigger"

    def get_parser(self, prog_name):
        parser = super(UpdateTrigger, self).get_parser(prog_name)
        parser.add_argument(
            "trigger_id",
            metavar="<TRIGGER ID>",
            help=_("Id of trigger to update.")
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help=_("A name to which the trigger will be renamed.")
        )
        parser.add_argument(
            "--properties",
            metavar="<key=value,key=value>",
            help=_("Properties of trigger which will be updated.")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        data = {}
        if parsed_args.name is not None:
            data['name'] = parsed_args.name
        if parsed_args.properties is not None:
            trigger_properties = utils.extract_properties(parsed_args)
            data['properties'] = trigger_properties
        try:
            trigger = osc_utils.find_resource(client.triggers,
                                              parsed_args.trigger_id)
            trigger = client.triggers.update(trigger.id, data)
        except exceptions.NotFound:
            raise exceptions.CommandError(
                "Trigger %s not found" % parsed_args.trigger_id)
        else:
            trigger._info.pop("links", None)
            return zip(*sorted(trigger._info.items()))


class DeleteTrigger(command.Command):
    _description = "Delete trigger"

    log = logging.getLogger(__name__ + ".DeleteTrigger")

    def get_parser(self, prog_name):
        parser = super(DeleteTrigger, self).get_parser(prog_name)
        parser.add_argument(
            'trigger',
            metavar='<trigger>',
            nargs="+",
            help=_('ID of trigger.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        failure_count = 0
        for trigger_id in parsed_args.trigger:
            try:
                trigger = osc_utils.find_resource(client.triggers, trigger_id)
                client.triggers.delete(trigger.id)
            except exceptions.NotFound:
                failure_count += 1
                self.log.error(
                    "Failed to delete '{0}'; trigger not found".
                    format(trigger_id))
        if failure_count == len(parsed_args.trigger):
            raise exceptions.CommandError(
                "Unable to find and delete any of the "
                "specified trigger.")

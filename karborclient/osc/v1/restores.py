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

"""Data protection V1 restore action implementations"""

import functools

from oslo_serialization import jsonutils
from oslo_utils import uuidutils

from osc_lib.command import command
from osc_lib import utils as osc_utils
from oslo_log import log as logging

from karborclient.common.apiclient import exceptions
from karborclient.i18n import _
from karborclient import utils


def format_restore(restore_info):
    for key in ('parameters', 'resources_status',
                'resources_reason'):
        if key not in restore_info:
            continue
        restore_info[key] = jsonutils.dumps(restore_info[key],
                                            indent=2, sort_keys=True)
    restore_info.pop("links", None)


class ListRestores(command.Lister):
    _description = _("List restores.")

    log = logging.getLogger(__name__ + ".ListRestores")

    def get_parser(self, prog_name):
        parser = super(ListRestores, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Include all projects (admin only)'),
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            help=_('Filter results by status'),
        )
        parser.add_argument(
            '--marker',
            metavar='<restore>',
            help=_('The last restore ID of the previous page'),
        )
        parser.add_argument(
            '--limit',
            type=int,
            metavar='<num-restores>',
            help=_('Maximum number of restores to display'),
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            default=None,
            help=_("Sort output by selected keys and directions(asc or desc), "
                   "multiple keys and directions can be "
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
            'status': parsed_args.status,
        }

        data = data_protection_client.restores.list(
            search_opts=search_opts, marker=parsed_args.marker,
            limit=parsed_args.limit, sort=parsed_args.sort)

        column_headers = ['Id', 'Project id', 'Provider id', 'Checkpoint id',
                          'Restore target', 'Parameters', 'Status']

        json_dumps = functools.partial(jsonutils.dumps,
                                       indent=2,
                                       sort_keys=True)
        formatters = {
            "Parameters": json_dumps,
        }
        return (column_headers,
                (osc_utils.get_item_properties(
                    s, column_headers, formatters=formatters,
                ) for s in data))


class ShowRestore(command.ShowOne):
    _description = "Shows restore details"

    def get_parser(self, prog_name):
        parser = super(ShowRestore, self).get_parser(prog_name)
        parser.add_argument(
            'restore',
            metavar="<restore>",
            help=_('The UUID of the restore.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        restore = osc_utils.find_resource(client.restores, parsed_args.restore)

        format_restore(restore._info)
        return zip(*sorted(restore._info.items()))


class CreateRestore(command.ShowOne):
    _description = "Creates a restore"

    def get_parser(self, prog_name):
        parser = super(CreateRestore, self).get_parser(prog_name)
        parser.add_argument(
            'provider_id',
            metavar='<provider_id>',
            help=_('The UUID of the provider.')
        )
        parser.add_argument(
            'checkpoint_id',
            metavar='<checkpoint_id>',
            help=_('The UUID of the checkpoint.')
        )
        parser.add_argument(
            '--restore_target',
            metavar='<restore_target>',
            help=_('The target of the restore operation.')
        )
        parser.add_argument(
            '--restore_username',
            metavar='<restore_username>',
            default=None,
            help=_('Username to restore target.')
        )
        parser.add_argument(
            '--restore_password',
            metavar='<restore_password>',
            default=None,
            help=_('Password to restore target.')
        )
        parser.add_argument(
            '--parameters-json',
            type=str,
            dest='parameters_json',
            metavar='<parameters>',
            default=None,
            help=_('Restore parameters in json format.')
        )
        parser.add_argument(
            '--parameters',
            action='append',
            metavar='resource_type=<type>[,resource_id=<id>,key=val,...]',
            default=[],
            help=_("Restore parameters, may be specified multiple times. "
                   "resource_type: type of resource to apply parameters. "
                   "resource_id: limit the parameters to a specific resource. "
                   "Other keys and values: according to provider\'s "
                   "restore schema.")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        if not uuidutils.is_uuid_like(parsed_args.provider_id):
            raise exceptions.CommandError(
                "Invalid provider id provided.")
        if not uuidutils.is_uuid_like(parsed_args.checkpoint_id):
            raise exceptions.CommandError(
                "Invalid checkpoint id provided.")

        restore_parameters = utils.extract_parameters(parsed_args)
        restore_auth = None
        if parsed_args.restore_target is not None:
            if parsed_args.restore_username is None:
                raise exceptions.CommandError(
                    "Must specify username for restore_target.")
            if parsed_args.restore_password is None:
                raise exceptions.CommandError(
                    "Must specify password for restore_target.")
            restore_auth = {
                'type': 'password',
                'username': parsed_args.restore_username,
                'password': parsed_args.restore_password,
            }
        restore = client.restores.create(parsed_args.provider_id,
                                         parsed_args.checkpoint_id,
                                         parsed_args.restore_target,
                                         restore_parameters, restore_auth)
        format_restore(restore._info)
        return zip(*sorted(restore._info.items()))

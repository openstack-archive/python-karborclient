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

"""Data protection V1 verification action implementations"""

import functools

from oslo_log import log as logging
from oslo_serialization import jsonutils
from oslo_utils import uuidutils

from osc_lib.command import command
from osc_lib import utils as osc_utils

from karborclient.common.apiclient import exceptions
from karborclient.i18n import _
from karborclient import utils


def format_verification(verification_info):
    for key in ('parameters', 'resources_status',
                'resources_reason'):
        if key not in verification_info:
            continue
        verification_info[key] = jsonutils.dumps(verification_info[key],
                                                 indent=2, sort_keys=True)
    verification_info.pop("links", None)


class ListVerifications(command.Lister):
    _description = _("List verifications.")

    log = logging.getLogger(__name__ + ".ListVerifications")

    def get_parser(self, prog_name):
        parser = super(ListVerifications, self).get_parser(prog_name)
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
            metavar='<verification>',
            help=_('The last verification ID of the previous page'),
        )
        parser.add_argument(
            '--limit',
            type=int,
            metavar='<num-verifications>',
            help=_('Maximum number of verifications to display'),
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

        data = data_protection_client.verifications.list(
            search_opts=search_opts, marker=parsed_args.marker,
            limit=parsed_args.limit, sort=parsed_args.sort)

        column_headers = ['Id', 'Project id', 'Provider id', 'Checkpoint id',
                          'Parameters', 'Status']

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


class ShowVerification(command.ShowOne):
    _description = "Shows verification details"

    def get_parser(self, prog_name):
        parser = super(ShowVerification, self).get_parser(prog_name)
        parser.add_argument(
            'verification',
            metavar="<verification>",
            help=_('The UUID of the verification.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        verification = osc_utils.find_resource(client.verifications,
                                               parsed_args.verification)

        format_verification(verification._info)
        return zip(*sorted(verification._info.items()))


class CreateVerification(command.ShowOne):
    _description = "Creates a verification"

    def get_parser(self, prog_name):
        parser = super(CreateVerification, self).get_parser(prog_name)
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
            '--parameters-json',
            type=str,
            dest='parameters_json',
            metavar='<parameters>',
            default=None,
            help=_('Verification parameters in json format.')
        )
        parser.add_argument(
            '--parameters',
            action='append',
            metavar='resource_type=<type>[,resource_id=<id>,key=val,...]',
            default=[],
            help=_("Verification parameters, may be specified multiple times. "
                   "resource_type: type of resource to apply parameters. "
                   "resource_id: limit the parameters to a specific resource. "
                   "Other keys and values: according to provider\'s "
                   "verification schema.")
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

        verification_parameters = utils.extract_parameters(parsed_args)
        verification = client.verifications.create(parsed_args.provider_id,
                                                   parsed_args.checkpoint_id,
                                                   verification_parameters)
        format_verification(verification._info)
        return zip(*sorted(verification._info.items()))

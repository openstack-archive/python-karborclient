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

"""Data protection V1 plan action implementations"""

from oslo_serialization import jsonutils
from oslo_utils import uuidutils

from osc_lib.command import command
from osc_lib import utils as osc_utils
from oslo_log import log as logging

from karborclient.common.apiclient import exceptions
from karborclient.i18n import _
from karborclient import utils


def format_plan(plan_info):
    for key in ('resources', 'parameters'):
        if key not in plan_info:
            continue
        plan_info[key] = jsonutils.dumps(plan_info[key],
                                         indent=2, sort_keys=True)
    plan_info.pop("links", None)


class ListPlans(command.Lister):
    _description = _("List plans.")

    log = logging.getLogger(__name__ + ".ListPlans")

    def get_parser(self, prog_name):
        parser = super(ListPlans, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Include all projects (admin only)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Filter results by plan name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Filter results by plan description'),
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            help=_('Filter results by status'),
        )
        parser.add_argument(
            '--marker',
            metavar='<plan>',
            help=_('The last plan ID of the previous page'),
        )
        parser.add_argument(
            '--limit',
            type=int,
            metavar='<num-plans>',
            help=_('Maximum number of plans to display'),
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
            'description': parsed_args.description,
            'status': parsed_args.status,
        }

        data = data_protection_client.plans.list(
            search_opts=search_opts, marker=parsed_args.marker,
            limit=parsed_args.limit, sort=parsed_args.sort)

        column_headers = ['Id', 'Name', 'Description', 'Provider id', 'Status']

        return (column_headers,
                (osc_utils.get_item_properties(
                    s, column_headers
                ) for s in data))


class ShowPlan(command.ShowOne):
    _description = "Shows plan details"

    def get_parser(self, prog_name):
        parser = super(ShowPlan, self).get_parser(prog_name)
        parser.add_argument(
            'plan',
            metavar="<plan>",
            help=_('The UUID of the plan.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        plan = osc_utils.find_resource(client.plans, parsed_args.plan)

        format_plan(plan._info)
        return zip(*sorted(plan._info.items()))


class CreatePlan(command.ShowOne):
    _description = "Creates a plan"

    def get_parser(self, prog_name):
        parser = super(CreatePlan, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('The name of the plan.')
        )
        parser.add_argument(
            'provider_id',
            metavar='<provider_id>',
            help=_('The UUID of the provider.')
        )
        parser.add_argument(
            'resources',
            metavar='<id=type=name=extra_info,id=type=name=extra_info>',
            help=_('Resource in list must be a dict when creating'
                   ' a plan. The keys of resource are id ,type, name and '
                   'extra_info. The extra_info field is optional.')
        )
        parser.add_argument(
            '--parameters-json',
            type=str,
            dest='parameters_json',
            metavar='<parameters>',
            default=None,
            help=_('Plan parameters in json format.')
        )
        parser.add_argument(
            '--parameters',
            action='append',
            metavar='resource_type=<type>[,resource_id=<id>,key=val,...]',
            default=[],
            help=_('Plan parameters, may be specified multiple times. '
                   'resource_type: type of resource to apply parameters. '
                   'resource_id: limit the parameters to a specific resource. '
                   'Other keys and values: according to provider\'s protect '
                   'schema.')
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('The description of the plan.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        if not uuidutils.is_uuid_like(parsed_args.provider_id):
            raise exceptions.CommandError(
                "Invalid provider id provided.")
        plan_resources = utils.extract_resources(parsed_args)
        utils.check_resources(client, plan_resources)
        plan_parameters = utils.extract_parameters(parsed_args)
        plan = client.plans.create(parsed_args.name, parsed_args.provider_id,
                                   plan_resources, plan_parameters,
                                   description=parsed_args.description)

        format_plan(plan._info)
        return zip(*sorted(plan._info.items()))


class UpdatePlan(command.ShowOne):
    _description = "Update a plan"

    def get_parser(self, prog_name):
        parser = super(UpdatePlan, self).get_parser(prog_name)
        parser.add_argument(
            "plan_id",
            metavar="<PLAN ID>",
            help=_("Id of plan to update.")
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help=_("A name to which the plan will be renamed.")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Description to which the plan will be updated.")
        )
        parser.add_argument(
            "--resources",
            metavar="<id=type=name,id=type=name>",
            help=_("Resources to which the plan will be updated.")
        )
        parser.add_argument(
            "--status",
            metavar="<suspended|started>",
            help=_("status to which the plan will be updated.")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        data = {}
        if parsed_args.name is not None:
            data['name'] = parsed_args.name
        if parsed_args.description is not None:
            data['description'] = parsed_args.description
        if parsed_args.resources is not None:
            plan_resources = utils.extract_resources(parsed_args)
            data['resources'] = plan_resources
        if parsed_args.status is not None:
            data['status'] = parsed_args.status
        try:
            plan = osc_utils.find_resource(client.plans,
                                           parsed_args.plan_id)
            plan = client.plans.update(plan.id, data)
        except exceptions.NotFound:
            raise exceptions.CommandError(
                "Plan %s not found" % parsed_args.plan_id)
        else:
            format_plan(plan._info)
            return zip(*sorted(plan._info.items()))


class DeletePlan(command.Command):
    _description = "Delete plan"

    def get_parser(self, prog_name):
        parser = super(DeletePlan, self).get_parser(prog_name)
        parser.add_argument(
            'plan',
            metavar='<plan>',
            nargs="+",
            help=_('ID of plan.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        failure_count = 0
        for plan_id in parsed_args.plan:
            try:
                plan = osc_utils.find_resource(client.plans, plan_id)
                client.plans.delete(plan.id)
            except exceptions.NotFound:
                failure_count += 1
                print("Failed to delete '{0}'; plan not "
                      "found".format(plan_id))
        if failure_count == len(parsed_args.plan):
            raise exceptions.CommandError(
                "Unable to find and delete any of the "
                "specified plan.")

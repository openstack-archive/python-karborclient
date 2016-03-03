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

import argparse

import os

from oslo_utils import uuidutils
from smaugclient.common import base
from smaugclient.common import utils
from smaugclient.openstack.common.apiclient import exceptions


@utils.arg('--all-tenants',
           dest='all_tenants',
           metavar='<0|1>',
           nargs='?',
           type=int,
           const=1,
           default=0,
           help='Shows details for all tenants. Admin only.')
@utils.arg('--all_tenants',
           nargs='?',
           type=int,
           const=1,
           help=argparse.SUPPRESS)
@utils.arg('--name',
           metavar='<name>',
           default=None,
           help='Filters results by a name. Default=None.')
@utils.arg('--status',
           metavar='<status>',
           default=None,
           help='Filters results by a status. Default=None.')
@utils.arg('--marker',
           metavar='<marker>',
           default=None,
           help='Begin returning plans that appear later in the plan '
                'list than that represented by this plan id. '
                'Default=None.')
@utils.arg('--limit',
           metavar='<limit>',
           default=None,
           help='Maximum number of volumes to return. Default=None.')
@utils.arg('--sort_key',
           metavar='<sort_key>',
           default=None,
           help=argparse.SUPPRESS)
@utils.arg('--sort_dir',
           metavar='<sort_dir>',
           default=None,
           help=argparse.SUPPRESS)
@utils.arg('--sort',
           metavar='<key>[:<direction>]',
           default=None,
           help=(('Comma-separated list of sort keys and directions in the '
                  'form of <key>[:<asc|desc>]. '
                  'Valid keys: %s. '
                  'Default=None.') % ', '.join(base.SORT_KEY_VALUES)))
@utils.arg('--tenant',
           type=str,
           dest='tenant',
           nargs='?',
           metavar='<tenant>',
           help='Display information from single tenant (Admin only).')
def do_plan_list(cs, args):
    """Lists all plans."""

    all_tenants = 1 if args.tenant else \
        int(os.environ.get("ALL_TENANTS", args.all_tenants))
    search_opts = {
        'all_tenants': all_tenants,
        'project_id': args.tenant,
        'name': args.name,
        'status': args.status,
    }

    if args.sort and (args.sort_key or args.sort_dir):
        raise exceptions.CommandError(
            'The --sort_key and --sort_dir arguments are deprecated and are '
            'not supported with --sort.')

    plans = cs.plans.list(search_opts=search_opts, marker=args.marker,
                          limit=args.limit, sort_key=args.sort_key,
                          sort_dir=args.sort_dir, sort=args.sort)

    key_list = ['Id', 'Name', 'Provider id', 'Status']

    if args.sort_key or args.sort_dir or args.sort:
        sortby_index = None
    else:
        sortby_index = 0
    utils.print_list(plans, key_list, exclude_unavailable=True,
                     sortby_index=sortby_index)


@utils.arg('name',
           metavar='<name>',
           help='Plan name.')
@utils.arg('provider_id',
           metavar='<provider_id>',
           help='ID of provider.')
@utils.arg('resources',
           metavar='<id=type,id=type>',
           help='Resource in list must be a dict when creating'
                ' a plan.The keys of resource are id and type.')
def do_plan_create(cs, args):
    """Create a plan."""
    plan_resources = _extract_resources(args)
    plan = cs.plans.create(args.name, args.provider_id, plan_resources)
    utils.print_dict(plan)


@utils.arg('plan',
           metavar='<plan>',
           help='ID of plan.')
def do_plan_show(cs, args):
    """Shows plan details."""
    plan = cs.plans.get(args.plan)
    utils.print_dict(plan.to_dict())


@utils.arg('plan',
           metavar='<plan>',
           nargs="+",
           help='ID of plan.')
def do_plan_delete(cs, args):
    """Delete plan."""
    failure_count = 0
    for plan_id in args.plan:
        try:
            plan = utils.find_resource(cs.plans, plan_id)
            cs.plans.delete(plan.id)
        except exceptions.NotFound:
            failure_count += 1
            print("Failed to delete '{0}'; plan not found".
                  format(plan_id))
    if failure_count == len(args.plan):
        raise exceptions.CommandError("Unable to find and delete any of the "
                                      "specified plan.")


@utils.arg("plan_id", metavar="<PLAN ID>",
           help="Id of plan to update.")
@utils.arg("--name", metavar="<name>",
           help="A name to which the plan will be renamed.")
@utils.arg("--resources", metavar="<id=type,id=type>",
           help="Resources to which the plan will be updated.")
@utils.arg("--status", metavar="<suspended|started>",
           help="status to which the plan will be updated.")
def do_plan_update(cs, args):
    """Updata a plan."""
    data = {}
    if args.name is not None:
        data['name'] = args.name
    if args.resources is not None:
        plan_resources = _extract_resources(args)
        data['resources'] = plan_resources
    if args.status is not None:
        data['status'] = args.status
    try:
        plan = utils.find_resource(cs.plans, args.plan_id)
        plan = cs.plans.update(plan.id, data)
    except exceptions.NotFound:
        raise exceptions.CommandError("Plan %s not found" % args.plan_id)
    else:
        utils.print_dict(plan.to_dict())


def _extract_resources(args):
    resources = []
    for data in args.resources.split(','):
        resource = {}
        if '=' in data:
            (resource_id, resource_type) = data.split('=', 1)
        else:
            raise exceptions.CommandError(
                "Unable to parse parameter resources.")

        resource["id"] = resource_id
        resource["type"] = resource_type
        resources.append(resource)
    return resources


@utils.arg('provider_id',
           metavar='<provider_id>',
           help='Provider id.')
@utils.arg('checkpoint_id',
           metavar='<checkpoint_id>',
           help='Checkpoint id.')
@utils.arg('restore_target',
           metavar='<restore_target>',
           help='Restore target.')
@utils.arg('--parameters',
           type=str,
           nargs='*',
           metavar='<key=value>',
           default=None,
           help='The parameters of a restore target.')
def do_restore_create(cs, args):
    """Create a restore."""
    if not uuidutils.is_uuid_like(args.provider_id):
        raise exceptions.CommandError(
            "Invalid provider id provided.")

    if not uuidutils.is_uuid_like(args.checkpoint_id):
        raise exceptions.CommandError(
            "Invalid checkpoint id provided.")

    if args.parameters is not None:
        restore_parameters = _extract_parameters(args)
    else:
        raise exceptions.CommandError(
            "checkpoint_id must be provided.")
    restore = cs.restores.create(args.provider_id, args.checkpoint_id,
                                 args.restore_target, restore_parameters)
    utils.print_dict(restore)


def _extract_parameters(args):
    parameters = {}
    for data in args.parameters:
        # unset doesn't require a val, so we have the if/else
        if '=' in data:
            (key, value) = data.split('=', 1)
        else:
            key = data
            value = None

        parameters[key] = value
    return parameters


@utils.arg('--all-tenants',
           dest='all_tenants',
           metavar='<0|1>',
           nargs='?',
           type=int,
           const=1,
           default=0,
           help='Shows details for all tenants. Admin only.')
@utils.arg('--all_tenants',
           nargs='?',
           type=int,
           const=1,
           help=argparse.SUPPRESS)
@utils.arg('--status',
           metavar='<status>',
           default=None,
           help='Filters results by a status. Default=None.')
@utils.arg('--marker',
           metavar='<marker>',
           default=None,
           help='Begin returning plans that appear later in the plan '
                'list than that represented by this plan id. '
                'Default=None.')
@utils.arg('--limit',
           metavar='<limit>',
           default=None,
           help='Maximum number of volumes to return. Default=None.')
@utils.arg('--sort_key',
           metavar='<sort_key>',
           default=None,
           help=argparse.SUPPRESS)
@utils.arg('--sort_dir',
           metavar='<sort_dir>',
           default=None,
           help=argparse.SUPPRESS)
@utils.arg('--sort',
           metavar='<key>[:<direction>]',
           default=None,
           help=(('Comma-separated list of sort keys and directions in the '
                  'form of <key>[:<asc|desc>]. '
                  'Valid keys: %s. '
                  'Default=None.') % ', '.join(base.SORT_KEY_VALUES)))
@utils.arg('--tenant',
           type=str,
           dest='tenant',
           nargs='?',
           metavar='<tenant>',
           help='Display information from single tenant (Admin only).')
def do_restore_list(cs, args):
    """Lists all restores."""

    all_tenants = 1 if args.tenant else \
        int(os.environ.get("ALL_TENANTS", args.all_tenants))
    search_opts = {
        'all_tenants': all_tenants,
        'project_id': args.tenant,
        'status': args.status,
    }

    if args.sort and (args.sort_key or args.sort_dir):
        raise exceptions.CommandError(
            'The --sort_key and --sort_dir arguments are deprecated and are '
            'not supported with --sort.')

    restores = cs.restores.list(search_opts=search_opts, marker=args.marker,
                                limit=args.limit, sort_key=args.sort_key,
                                sort_dir=args.sort_dir, sort=args.sort)

    key_list = ['Id', 'Project id', 'Provider id', 'Checkpoint id',
                'Restore target', 'Parameters', 'Status']

    if args.sort_key or args.sort_dir or args.sort:
        sortby_index = None
    else:
        sortby_index = 0
    utils.print_list(restores, key_list, exclude_unavailable=True,
                     sortby_index=sortby_index)


@utils.arg('restore',
           metavar='<restore>',
           help='ID of restore.')
def do_restore_show(cs, args):
    """Shows restore details."""
    restore = cs.restores.get(args.restore)
    utils.print_dict(restore.to_dict())

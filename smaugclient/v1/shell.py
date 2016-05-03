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
           metavar='<id=type=name,id=type=name>',
           help='Resource in list must be a dict when creating'
                ' a plan.The keys of resource are id and type.')
@utils.arg('--parameters',
           type=str,
           nargs='*',
           metavar='<key=value>',
           default=None,
           help='The parameters of a plan.')
def do_plan_create(cs, args):
    """Create a plan."""
    plan_resources = _extract_resources(args)
    if args.parameters is not None:
        plan_parameters = _extract_parameters(args)
    else:
        raise exceptions.CommandError(
            "parameters must be provided.")
    plan = cs.plans.create(args.name, args.provider_id, plan_resources,
                           plan_parameters)
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
            (resource_id, resource_type, resource_name) = data.split('=', 2)
        else:
            raise exceptions.CommandError(
                "Unable to parse parameter resources.")

        resource["id"] = resource_id
        resource["type"] = resource_type
        resource["name"] = resource_name
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
            "parameters must be provided.")
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


def do_protectable_list(cs, args):
    """Lists all protectables type."""

    protectables = cs.protectables.list()

    key_list = ['Protectable type']

    utils.print_list(protectables, key_list, exclude_unavailable=True)


@utils.arg('protectable_type',
           metavar='<protectable_type>',
           help='Protectable type.')
def do_protectable_show(cs, args):
    """Shows protectable type details."""
    protectable = cs.protectables.get(args.protectable_type)
    utils.print_dict(protectable.to_dict())


@utils.arg('protectable_id',
           metavar='<protectable_id>',
           help='Protectable instance id.')
@utils.arg('protectable_type',
           metavar='<protectable_type>',
           help='Protectable type.')
def do_protectable_show_instance(cs, args):
    """Shows instance details."""
    instance = cs.protectables.get_instance(args.protectable_type,
                                            args.protectable_id)
    utils.print_dict(instance.to_dict())


@utils.arg('protectable_type',
           metavar='<protectable_type>',
           help='Type of protectable.')
@utils.arg('--type',
           metavar='<type>',
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
def do_protectable_list_instances(cs, args):
    """Lists all protectable instances."""

    search_opts = {
        'type': args.type,
    }

    if args.sort and (args.sort_key or args.sort_dir):
        raise exceptions.CommandError(
            'The --sort_key and --sort_dir arguments are deprecated and are '
            'not supported with --sort.')

    instances = cs.protectables.list_instances(
        args.protectable_type, search_opts=search_opts,
        marker=args.marker, limit=args.limit,
        sort_key=args.sort_key,
        sort_dir=args.sort_dir, sort=args.sort)

    key_list = ['Id', 'Type', 'Dependent resources']

    if args.sort_key or args.sort_dir or args.sort:
        sortby_index = None
    else:
        sortby_index = 0
    utils.print_list(instances, key_list, exclude_unavailable=True,
                     sortby_index=sortby_index)


@utils.arg('provider_id',
           metavar='<provider_id>',
           help='Id of provider.')
def do_provider_show(cs, args):
    """Shows provider details."""
    provider = cs.providers.get(args.provider_id)
    utils.print_dict(provider.to_dict())


@utils.arg('--name',
           metavar='<name>',
           default=None,
           help='Filters results by a name. Default=None.')
@utils.arg('--description',
           metavar='<description>',
           default=None,
           help='Filters results by a description. Default=None.')
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
def do_provider_list(cs, args):
    """Lists all providers."""

    search_opts = {
        'name': args.name,
        'description': args.description,
    }

    if args.sort and (args.sort_key or args.sort_dir):
        raise exceptions.CommandError(
            'The --sort_key and --sort_dir arguments are deprecated and are '
            'not supported with --sort.')

    providers = cs.providers.list(search_opts=search_opts, marker=args.marker,
                                  limit=args.limit, sort_key=args.sort_key,
                                  sort_dir=args.sort_dir, sort=args.sort)

    key_list = ['Id', 'Name', 'Description', 'Extended_info_schema']

    if args.sort_key or args.sort_dir or args.sort:
        sortby_index = None
    else:
        sortby_index = 0
    utils.print_list(providers, key_list, exclude_unavailable=True,
                     sortby_index=sortby_index)


@utils.arg('provider_id',
           metavar='<provider_id>',
           help='ID of provider.')
@utils.arg('plan_id',
           metavar='<plan_id>',
           help='ID of plan.')
def do_checkpoint_create(cs, args):
    """Create a checkpoint."""
    checkpoint = cs.checkpoints.create(args.provider_id, args.plan_id)
    utils.print_dict(checkpoint)


@utils.arg('provider_id',
           metavar='<provider_id>',
           help='ID of provider.')
@utils.arg('--status',
           metavar='<status>',
           default=None,
           help='Filters results by a status. Default=None.')
@utils.arg('--project_id',
           metavar='<project_id>',
           default=None,
           help='Filters results by a project id. Default=None.')
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
def do_checkpoint_list(cs, args):
    """Lists all checkpoints."""

    search_opts = {
        'status': args.status,
        'project_id': args.project_id,
    }

    if args.sort and (args.sort_key or args.sort_dir):
        raise exceptions.CommandError(
            'The --sort_key and --sort_dir arguments are deprecated and are '
            'not supported with --sort.')

    checkpoints = cs.checkpoints.list(
        provider_id=args.provider_id, search_opts=search_opts,
        marker=args.marker, limit=args.limit, sort_key=args.sort_key,
        sort_dir=args.sort_dir, sort=args.sort)

    key_list = ['Id', 'Project id', 'Status', 'Protection plan']

    if args.sort_key or args.sort_dir or args.sort:
        sortby_index = None
    else:
        sortby_index = 0
    utils.print_list(checkpoints, key_list, exclude_unavailable=True,
                     sortby_index=sortby_index)


@utils.arg('provider_id',
           metavar='<provider_id>',
           help='Id of provider.')
@utils.arg('checkpoint_id',
           metavar='<checkpoint_id>',
           help='Id of checkpoint.')
def do_checkpoint_show(cs, args):
    """Shows checkpoint details."""
    checkpoint = cs.checkpoints.get(args.provider_id, args.checkpoint_id)
    utils.print_dict(checkpoint.to_dict())


@utils.arg('provider_id',
           metavar='<provider_id>',
           help='Id of provider.')
@utils.arg('checkpoint',
           metavar='<checkpoint>',
           nargs="+",
           help='ID of checkpoint.')
def do_checkpoint_delete(cs, args):
    """Delete checkpoints."""
    failure_count = 0
    for checkpoint_id in args.checkpoint:
        try:
            checkpoint = cs.checkpoints.get(args.provider_id,
                                            checkpoint_id)
            cs.checkpoints.delete(checkpoint.provider_id, checkpoint.id)
        except exceptions.NotFound:
            failure_count += 1
            print("Failed to delete '{0}'; checkpoint not found".
                  format(checkpoint_id))
    if failure_count == len(args.checkpoint):
        raise exceptions.CommandError("Unable to find and delete any of the "
                                      "specified checkpoint.")


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
@utils.arg('--type',
           metavar='<type>',
           default=None,
           help='Filters results by a type. Default=None.')
@utils.arg('--properties',
           metavar='<properties>',
           default=None,
           help='Filters results by a properties. Default=None.')
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
def do_trigger_list(cs, args):
    """Lists all triggers."""

    all_tenants = 1 if args.tenant else \
        int(os.environ.get("ALL_TENANTS", args.all_tenants))
    search_opts = {
        'all_tenants': all_tenants,
        'project_id': args.tenant,
        'name': args.name,
        'type': args.type,
        'properties': args.properties,
    }

    if args.sort and (args.sort_key or args.sort_dir):
        raise exceptions.CommandError(
            'The --sort_key and --sort_dir arguments are deprecated and are '
            'not supported with --sort.')

    triggers = cs.triggers.list(search_opts=search_opts, marker=args.marker,
                                limit=args.limit, sort_key=args.sort_key,
                                sort_dir=args.sort_dir, sort=args.sort)

    key_list = ['Id', 'Name', 'Type', 'Properties']

    if args.sort_key or args.sort_dir or args.sort:
        sortby_index = None
    else:
        sortby_index = 0
    utils.print_list(triggers, key_list, exclude_unavailable=True,
                     sortby_index=sortby_index)


@utils.arg('name',
           metavar='<name>',
           help='Trigger name.')
@utils.arg('type',
           metavar='<type>',
           help='Type of trigger.')
@utils.arg('properties',
           metavar='<key=value;key=value>',
           help='Properties of trigger.')
def do_trigger_create(cs, args):
    """Create a trigger."""
    trigger_properties = _extract_properties(args)
    trigger = cs.triggers.create(args.name, args.type, trigger_properties)
    utils.print_dict(trigger)


def _extract_properties(args):
    properties = {}
    for data in args.properties.split(':'):
        if '=' in data:
            (resource_key, resource_value) = data.split('=', 1)
        else:
            raise exceptions.CommandError(
                "Unable to parse parameter properties.")

        properties[resource_key] = resource_value
    return properties


@utils.arg('trigger',
           metavar='<trigger>',
           help='ID of trigger.')
def do_trigger_show(cs, args):
    """Shows trigger details."""
    trigger = cs.triggers.get(args.trigger)
    utils.print_dict(trigger.to_dict())


@utils.arg('trigger',
           metavar='<trigger>',
           nargs="+",
           help='ID of trigger.')
def do_trigger_delete(cs, args):
    """Delete trigger."""
    failure_count = 0
    for trigger_id in args.trigger:
        try:
            trigger = utils.find_resource(cs.triggers, trigger_id)
            cs.triggers.delete(trigger.id)
        except exceptions.NotFound:
            failure_count += 1
            print("Failed to delete '{0}'; trigger not found".
                  format(trigger_id))
    if failure_count == len(args.trigger):
        raise exceptions.CommandError("Unable to find and delete any of the "
                                      "specified trigger.")


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
@utils.arg('--operation_type',
           metavar='<operation_type>',
           default=None,
           help='Filters results by a type. Default=None.')
@utils.arg('--trigger_id',
           metavar='<trigger_id>',
           default=None,
           help='Filters results by a trigger id. Default=None.')
@utils.arg('--marker',
           metavar='<marker>',
           default=None,
           help='Begin returning resources that appear later in the '
                'list than that represented by this id. '
                'Default=None.')
@utils.arg('--limit',
           metavar='<limit>',
           default=None,
           help='Maximum number to return. Default=None.')
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
def do_scheduledoperation_list(cs, args):
    """Lists all scheduledoperations."""

    all_tenants = 1 if args.tenant else \
        int(os.environ.get("ALL_TENANTS", args.all_tenants))
    search_opts = {
        'all_tenants': all_tenants,
        'project_id': args.tenant,
        'name': args.name,
        'operation_type': args.type,
        'trigger_id': args.trigger_id,
    }

    if args.sort and (args.sort_key or args.sort_dir):
        raise exceptions.CommandError(
            'The --sort_key and --sort_dir arguments are deprecated and are '
            'not supported with --sort.')

    scheduledoperations = cs.scheduled_operations.list(
        search_opts=search_opts, marker=args.marker, limit=args.limit,
        sort_key=args.sort_key, sort_dir=args.sort_dir, sort=args.sort)

    key_list = ['Id', 'Name', 'OperationType', 'TriggerId',
                'OperationDefinition']

    if args.sort_key or args.sort_dir or args.sort:
        sortby_index = None
    else:
        sortby_index = 0
    utils.print_list(scheduledoperations, key_list, exclude_unavailable=True,
                     sortby_index=sortby_index)


@utils.arg('name',
           metavar='<name>',
           help='Trigger name.')
@utils.arg('operation_type',
           metavar='<operation_type>',
           help='Operation Type of scheduled operation.')
@utils.arg('trigger_id',
           metavar='<trigger_id>',
           help='Trigger id of scheduled operation.')
@utils.arg('operation_definition',
           metavar='<key=value;key=value>',
           help='Operation definition of scheduled operation.')
def do_scheduledoperation_create(cs, args):
    """Create a scheduled operation."""
    operation_definition = _extract_operation_definition(args)
    scheduledoperation = cs.scheduled_operations.create(args.name,
                                                        args.operation_type,
                                                        args.trigger_id,
                                                        operation_definition)
    utils.print_dict(scheduledoperation)


def _extract_operation_definition(args):
    operation_definition = {}
    for data in args.operation_definition.split(':'):
        if '=' in data:
            (resource_key, resource_value) = data.split('=', 1)
        else:
            raise exceptions.CommandError(
                "Unable to parse parameter operation_definition.")

        operation_definition[resource_key] = resource_value
    return operation_definition


@utils.arg('scheduledoperation',
           metavar='<scheduledoperation>',
           help='ID of scheduled operation.')
def do_scheduledoperation_show(cs, args):
    """Shows scheduledoperation details."""
    scheduledoperation = cs.scheduledoperations.get(args.scheduledoperation)
    utils.print_dict(scheduledoperation.to_dict())


@utils.arg('scheduledoperation',
           metavar='<scheduledoperation>',
           nargs="+",
           help='ID of scheduled operation.')
def do_scheduledoperation_delete(cs, args):
    """Delete a scheduled operation."""
    failure_count = 0
    for scheduledoperation_id in args.scheduledoperation:
        try:
            scheduledoperation = utils.find_resource(cs.scheduledoperations,
                                                     scheduledoperation_id)
            cs.scheduledoperations.delete(scheduledoperation.id)
        except exceptions.NotFound:
            failure_count += 1
            print("Failed to delete '{0}'; scheduledoperation not found".
                  format(scheduledoperation_id))
    if failure_count == len(args.scheduledoperation):
        raise exceptions.CommandError("Unable to find and delete any of the "
                                      "specified scheduled operation.")

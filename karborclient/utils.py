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

from oslo_serialization import jsonutils
from oslo_utils import uuidutils

from karborclient.common.apiclient import exceptions


def extract_resources(args):
    resources = []
    for data in args.resources.split(','):
        if '=' in data and len(data.split('=')) in [3, 4]:
            resource = dict(zip(['id', 'type', 'name', 'extra_info'],
                                data.split('=')))
            if resource.get('extra_info'):
                resource['extra_info'] = jsonutils.loads(
                    resource.get('extra_info'))
        else:
            raise exceptions.CommandError(
                "Unable to parse parameter resources. "
                "The keys of resource are id , type, name and "
                "extra_info. The extra_info field is optional.")
        resources.append(resource)
    return resources


def check_resources(cs, resources):
    # check the resource whether it is available
    for resource in resources:
        try:
            instance = cs.protectables.get_instance(
                resource["type"], resource["id"])
        except exceptions.NotFound:
            raise exceptions.CommandError(
                "The resource: %s can not be found." % resource["id"])
        else:
            if instance is None:
                raise exceptions.CommandError(
                    "The resource: %s is invalid." % resource["id"])


def extract_parameters(args):
    if all((args.parameters, args.parameters_json)):
        raise exceptions.CommandError(
            "Must provide parameters or parameters-json, not both")
    if not any((args.parameters, args.parameters_json)):
        return {}

    if args.parameters_json:
        return jsonutils.loads(args.parameters_json)
    parameters = {}
    for resource_params in args.parameters:
        resource_type = None
        resource_id = None
        parameter = {}
        for param_kv in resource_params.split(','):
            try:
                key, value = param_kv.split('=')
            except Exception:
                raise exceptions.CommandError(
                    'parameters must be in the form: key1=val1,key2=val2,...'
                )
            if key == "resource_type":
                resource_type = value
            elif key == "resource_id":
                if not uuidutils.is_uuid_like(value):
                    raise exceptions.CommandError('resource_id must be a uuid')
                resource_id = value
            else:
                parameter[key] = value
        if resource_type is None:
            raise exceptions.CommandError(
                'Must specify resource_type for parameters'
            )
        if resource_id is None:
            resource_key = resource_type
        else:
            resource_key = "%s#%s" % (resource_type, resource_id)
        parameters[resource_key] = parameter

    return parameters


def extract_instances_parameters(args):
    parameters = {}
    for parameter in args.parameters:
        if '=' in parameter:
            (key, value) = parameter.split('=', 1)
        else:
            key = parameter
            value = None

        parameters[key] = value
    return parameters


def extract_extra_info(args):
    checkpoint_extra_info = {}
    for data in args.extra_info:
        # unset doesn't require a val, so we have the if/else
        if '=' in data:
            (key, value) = data.split('=', 1)
        else:
            key = data
            value = None

        checkpoint_extra_info[key] = value
    return checkpoint_extra_info


def extract_properties(args):
    properties = {}
    if args.properties is None:
        return properties
    for data in args.properties.split(','):
        if '=' in data:
            (resource_key, resource_value) = data.split('=', 1)
        else:
            raise exceptions.CommandError(
                "Unable to parse parameter properties.")

        properties[resource_key] = resource_value
    return properties


def extract_operation_definition(args):
    operation_definition = {}
    for data in args.operation_definition.split(','):
        if '=' in data:
            (resource_key, resource_value) = data.split('=', 1)
        else:
            raise exceptions.CommandError(
                "Unable to parse parameter operation_definition.")

        operation_definition[resource_key] = resource_value
    return operation_definition

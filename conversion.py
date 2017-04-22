#!/usr/bin/env python3

import avango
import avango.gua
import re

FIELD_BLACKLIST = [
    'BoundingBox',
    'Children',
    'Geometry',
    'Material', # TODO: support materials
    'Parent',
    'Path',
    'Transform',
    'WorldTransform'
]


def av_gua_to_json_type(var):
    if type(var) in [str, int, float, bool]:
        return var
    elif type(var) == avango.gua.Vec3:
        return [var.x, var.y, var.z]
    elif type(var) == avango.gua.Vec4:
        return [var.x, var.y, var.z, var.w]
    elif type(var) == avango.gua.Quat:
        return [var.x, var.y, var.z, var.w]
    elif type(var) == avango.gua.Color:
        return [var.r, var.g, var.b]
    elif type(var) == avango.gua.Material:
        return {
            'Name': var.Name.value,
            'ShaderName': var.ShaderName.value,
            'EnableBackfaceCulling': var.EnableBackfaceCulling.value
            }
    elif type(var) in [avango._avango.MFString_wrapper,
                       avango._avango.MFFloat_wrapper]:
        return [item for item in var]
    else:
        raise TypeError(
            'There is no conversion from type {} to a json-compatible type'
                .format(type(var).__name__))


def node_to_dict(node, id, parent_id):
    '''Converts an avango-gua node to a python dictionary'''

    # set some values that all nodes share
    d = {
        'id': id,
        'parent': parent_id,
        'type': type(node).__name__,
        'trans': av_gua_to_json_type(node.Transform.value.get_translate()),
        'rot': av_gua_to_json_type(
            node.Transform.value.get_rotate_scale_corrected()),
        'scale': av_gua_to_json_type(node.Transform.value.get_scale()),
        'fields': {}
    }

    if type(node).__name__ == 'TriMeshNode':
        # extract mesh filename from the geometry-field
        match = re.search('TriMesh\|(.*?)\|', node.Geometry.value)
        filename = match.group(1)
        d['filename'] = filename

    # iterate over all the fields that are not already covered above and store
    # their values
    for i in range(node.get_num_fields()):
        field_name = node.get_field_name(i)
        if not field_name in FIELD_BLACKLIST:
            d['fields'][field_name] = av_gua_to_json_type(node.get_field(i).value)

    return d


def dict_to_node(d):
    '''Converts a dictionary read from json to an avango-gua node'''

    if d['type'] == 'TriMeshNode':
        loader = avango.gua.nodes.TriMeshLoader()
        node = loader.create_geometry_from_file(
            d['fields']['Name'], d['filename'])
    else:
        node = getattr(avango.gua.nodes, d['type'])()

    # read field values
    for field_name, field_value in d['fields'].items():
        if not node.has_field(field_name):
            raise AttributeError('Node of type "{}" has no field "{}"'.format(
                d['type'], field_name))

        field_type = type(getattr(node, field_name).value)
        if type(field_value) in [str, int, float, bool]:
            getattr(node, field_name).value = field_value
        elif field_type in [avango._avango.MFString_wrapper,
                            avango._avango.MFFloat_wrapper]:
            getattr(node, field_name).value = field_value
        elif field_type:
            getattr(node, field_name).value = field_type(*field_value)
        else:
            raise TypeError('Unable to set value of field {} with type "{}"'
                .format(field_name, field_type))

    return node, d['id'], d['parent']

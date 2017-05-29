#!/usr/bin/env python3

import avango
import avango.gua
from pydoc import locate
import itertools
import re

FIELD_BLACKLIST = [
    'BoundingBox',
    'Children',
    'Geometry',
    'Material',  # TODO: support materials
    'Parent',
    'Path',
    'WorldTransform'
]

SIMPLE_FIELD_TYPES = [
    pre + typename
    for pre, typename in itertools.product(
        ['SF', 'MF'], ['Int', 'UInt', 'Bool', 'Float', 'String'])
]


def serialize_field_value(value):
    if type(value) in [str, int, float, bool]:
        return value
    elif type(value) == avango.gua.Vec3:
        return [value.x, value.y, value.z]
    elif type(value) == avango.gua.Vec4:
        return [value.x, value.y, value.z, value.w]
    elif type(value) == avango.gua.Quat:
        return [value.x, value.y, value.z, value.w]
    elif type(value) == avango.gua.Mat4:
        return [
            value.get_element(row, col) for row in range(4) for col in range(4)
        ]
    elif type(value) == avango.gua.Color:
        return [value.r, value.g, value.b]
    elif type(value) == avango.gua.Material:
        return {
            'Name': value.Name.value,
            'ShaderName': value.ShaderName.value,
            'EnableBackfaceCulling': value.EnableBackfaceCulling.value
        }
    elif type(value) in [avango.MFString_wrapper, avango.MFFloat_wrapper]:
        return [item for item in value]
    else:
        raise TypeError(
            'There is no conversion from type {} to a json-compatible type'
            .format(type(value).__name__))


def node_to_dict(node, id, parent_id):
    '''Converts an avango-gua node to a python dictionary'''

    # set some values that all nodes share
    d = {
        'id': id,
        'parent': parent_id,
        'type': type(node).__name__,
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
        name = node.get_field_name(i)
        if not name in FIELD_BLACKLIST:
            field = node.get_field(i)
            value = node.get_field(i).value
            d['fields'][name] = {
                'type': '{}.{}'.format(field.__module__, type(field).__name__),
                'value': serialize_field_value(value)
            }

    return d


def dict_to_node(d):
    '''Converts a dictionary read from json to an avango-gua node'''

    if d['type'] == 'TriMeshNode':
        loader = avango.gua.nodes.TriMeshLoader()
        node = loader.create_geometry_from_file(d['fields']['Name']['value'],
                                                d['filename'])
    else:
        node = getattr(avango.gua.nodes, d['type'])()

    # read field values
    for field_name, data in d['fields'].items():
        full_field_type = data['type']
        field_type = full_field_type.split('.')[-1]
        field_value = data['value']

        # node lacks this field, create it first
        if not node.has_field(field_name):
            node.add_field(locate(full_field_type)(), field_name)

        field_value_type = type(getattr(node, field_name).value)

        if field_type in SIMPLE_FIELD_TYPES:
            getattr(node, field_name).value = field_value
        elif field_type == 'SFMatrix4':
            mat = avango.gua.Mat4()
            for i, value in enumerate(field_value):
                row = i // 4
                col = i % 4
                mat.set_element(row, col, value)
            getattr(node, field_name).value = mat
        elif field_value_type:
            # this type was not handled yet; as a last resort, try to create
            # the type by passing all given values as parameters to its
            # default constructor
            getattr(node, field_name).value = field_value_type(*field_value)
        else:
            raise TypeError('Unable to set value of field {} with type "{}"'
                            .format(field_name, field_type))

    return node, d['id'], d['parent']

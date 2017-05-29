#!/usr/bin/env python3

import itertools
from pydoc import locate
import json

import avango
import avango.gua

from .conversion import mat_from_list

SIMPLE_FIELD_TYPES = [
    pre + typename
    for pre, typename in itertools.product(
        ['SF', 'MF'], ['Int', 'UInt', 'Bool', 'Float', 'String'])
]


def set_field_value(node, field_name, field_type, field_value):
    field_value_type = type(getattr(node, field_name).value)

    # simple field types can be set directly
    if field_type in SIMPLE_FIELD_TYPES:
        getattr(node, field_name).value = field_value
    elif field_type == 'SFMatrix4' and type(field_value) == list:
        getattr(node, field_name).value = mat_from_list(field_value)
    elif field_value_type:
        # this type was not handled yet; as a last resort, try to create
        # the type by passing all given values as parameters to its
        # default constructor
        getattr(node, field_name).value = field_value_type(*field_value)
    else:
        raise TypeError('Unable to set value of field {} with type "{}"'
                        .format(field_name, field_type))


def create_node_from_json(json, loader_flags=avango.gua.LoaderFlags.DEFAULTS):
    '''Creates a scene graph node from a json dictionary'''

    if json['type'] == 'TriMeshNode':
        loader = avango.gua.nodes.TriMeshLoader()
        node = loader.create_geometry_from_file(
            json['fields']['Name']['value'], json['filename'], loader_flags)
    else:
        node = getattr(avango.gua.nodes, json['type'])()

    # read field values
    for field_name, data in json['fields'].items():
        # field type with module qualifiers
        full_field_type = data['type']
        # field type without module qualifiers
        field_type = full_field_type.split('.')[-1]

        field_value = data['value']

        # the field does not exist by default; create it first
        if not node.has_field(field_name):
            node.add_field(locate(full_field_type)(), field_name)

        set_field_value(node, field_name, field_type, field_value)

    return node, json['id'], json['parent']


def import_scenegraph(filename,
                      name='scenegraph',
                      loader_flags=avango.gua.LoaderFlags.DEFAULTS):
    '''Reads a previously exported scene graph from a json-file'''

    graph = avango.gua.nodes.SceneGraph(Name=name)
    import_subtree(filename, graph.Root.value, loader_flags)
    return graph


def import_subtree(filename,
                   node,
                   loader_flags=avango.gua.LoaderFlags.DEFAULTS):
    '''Reads a subtree of the given scene graph node stored as a json-file'''

    # dictionary to map node ids to actual nodes;
    # fill initially with given node
    nodes = {0: node}

    # load graph from json of given file name
    with open(filename, 'r') as json_file:
        for line in json_file:
            # parse json line to node
            crrnt_node, id, parent_id = create_node_from_json(
                json.loads(line), loader_flags)

            # store node by id
            nodes[id] = crrnt_node
            # append to its parent
            nodes[parent_id].Children.value.append(crrnt_node)

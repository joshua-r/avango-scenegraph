#!/usr/bin/env python3

import avango
import avango.gua
import json

from collections import deque

FIELD_BLACKLIST = [
    'BoundingBox',
    'Children',
    'Parent',
    'Path',
    'Transform',
    'WorldTransform'
]


def to_json_type(var):
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
    d = {
        'ID': id,
        'Parent': parent_id,
        'Type': type(node).__name__,
        'Trans': to_json_type(node.Transform.value.get_translate()),
        'Rot': to_json_type(node.Transform.value.get_rotate_scale_corrected()),
        'Scale': to_json_type(node.Transform.value.get_scale()),
    }
    for i in range(node.get_num_fields()):
        field_name = node.get_field_name(i)
        if not field_name in FIELD_BLACKLIST:
            d[field_name] = to_json_type(node.get_field(i).value)

    return d


def export_scenegraph(graph, filename,
                      type_blacklist=['CameraNode', 'ScreenNode']):
    '''Writes the given avango-gua scene graph into a json-file'''

    # counter as unique id for every node to store relations between nodes
    node_id = 0

    # holds tuples of node and parent-id for nodes to be stored
    # initialized with root node that has no parent
    queue = deque([(graph.Root.value, -1)])

    # store graph as json into file with of given filename
    with open(filename, 'w') as json_file:
        while len(queue):
            # retrieve current node (FIFO)
            node, parent_id = queue.popleft()

            # write node as one json-object as one line into the file
            json_file.write(json.dumps(
                obj=node_to_dict(node=node, id=node_id, parent_id=parent_id),
                sort_keys=True))
            json_file.write('\n')

            # add the node's children to the queue and store the current node's
            # id as their parent-id
            queue.extend([(child, node_id)
                for child in node.Children.value
                    if not type(child).__name__ in type_blacklist])

            # increase the counter to assign the next node the next free id
            node_id += 1

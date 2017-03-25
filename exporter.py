#!/usr/bin/env python3

import avango
import avango.gua
import json

from collections import deque


def vec3_to_list(vec):
    '''Converts an avango-gua Vec3 to a list of its components'''
    return [vec.x, vec.y, vec.z]


def quat_to_list(quat):
    '''Converts an avango-gua Quaternion to a list containing x, y, z and w'''
    return [quat.x, quat.y, quat.z, quat.w]


def node_to_dict(node, id, parent_id):
    '''Converts an avango-gua node to a python dictionary'''
    return {
        'name': node.Name.value,
        'trans': vec3_to_list(node.Transform.value.get_translate()),
        'rot': quat_to_list(node.Transform.value.get_rotate_scale_corrected()),
        'scale': vec3_to_list(node.Transform.value.get_scale()),
        'type': type(node).__name__,
        'id': id,
        'parent': parent_id,
    }


def export_scenegraph(graph, filename):
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
            queue.extend([(child, node_id) for child in node.Children.value])

            # increase the counter to assign the next node the next free id
            node_id += 1

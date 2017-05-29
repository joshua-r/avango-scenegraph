#!/usr/bin/env python3

from collections import deque
import json
import re

from .conversion import serialize_field_value


FIELD_BLACKLIST = [
    'BoundingBox',
    'Children',
    'Geometry',
    'Material',  # TODO: support materials
    'Parent',
    'Path',
    'WorldTransform'
]

TYPE_BLACKLIST = ['CameraNode', 'ScreenNode']


def serialize_node(node, id, parent_id):
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


def export_scenegraph(filename, graph):
    '''Writes the given scene graph into a json-file'''
    export_subtree(filename, graph.Root.value)


def export_subtree(filename, node):
    '''Writes the subtree of the given scene graph node into a json-file

    Arguments:
    node -- the scene graph node whose subtree is stored (excluding the node
            itself)
    '''

    # counter as unique id for every node to store relations between nodes;
    # starts at one because given node is 0
    node_id = 1

    # holds tuples of node and parent-id for nodes to be stored
    queue = deque()

    # function to add tuples of the form (node, parent_id) to the queue
    def add_nodes_to_queue(nodes):
        queue.extend([(node, parent) for node, parent in nodes
                      if not type(node).__name__ in TYPE_BLACKLIST])

    # initialize queue with child nodes of the given node
    add_nodes_to_queue([(child, 0) for child in node.Children.value])

    # store graph as json into file with of given filename
    with open(filename, 'w') as json_file:
        while len(queue):
            # retrieve current node (FIFO)
            node, parent_id = queue.popleft()

            # write node as one json-object as one line into the file
            json_file.write(
                json.dumps(
                    obj=serialize_node(
                        node=node, id=node_id, parent_id=parent_id),
                    sort_keys=True))
            json_file.write('\n')

            # add the node's children to the queue and store the current node's
            # id as their parent-id
            add_nodes_to_queue([(child, node_id)
                                for child in node.Children.value])

            # increase the counter to assign the next node the next free id
            node_id += 1

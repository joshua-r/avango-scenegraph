#!/usr/bin/env python3

import json

import avango
import avango.gua

from .conversion import dict_to_node


def import_scenegraph(filename, name='scenegraph'):
    '''Reads a previously exported scene graph from a json-file'''

    graph = avango.gua.nodes.SceneGraph(Name=name)
    import_subtree(filename, graph.Root.value)
    return graph


def import_subtree(filename, node):
    '''Reads a subtree of the given scene graph node stored as a json-file'''

    # dictionary to map node ids to actual nodes; fill initially with given node
    nodes = {0: node}

    # load graph from json of given file name
    with open(filename, 'r') as json_file:
        for line in json_file:
            # parse json line to node
            crrnt_node, id, parent_id = dict_to_node(json.loads(line))

            # store node by id
            nodes[id] = crrnt_node
            # append to its parent
            nodes[parent_id].Children.value.append(crrnt_node)

#!/usr/bin/env python3

import json

import avango
import avango.gua

from .conversion import dict_to_node


def import_scenegraph(filename, name='scenegraph'):
    '''Reads a previously exported avango-gua scene graph from a json-file'''
    graph = avango.gua.nodes.SceneGraph(Name=name)

    # dictionary to map node ids to actual nodes; fill initially with root
    nodes = {0: graph.Root.value}

    # load graph from json of given file name
    with open(filename, 'r') as json_file:
        for line in json_file:
            # parse json line to node
            node, id, parent_id = dict_to_node(json.loads(line))

            # store node by id
            nodes[id] = node
            # append to its parent
            nodes[parent_id].Children.value.append(node)

    return graph

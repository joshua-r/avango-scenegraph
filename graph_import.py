#!/usr/bin/env python3

from collections import deque
import json

import avango
import avango.gua

from .conversion import dict_to_node

def import_scenegraph(filename, name='scenegraph',
                      type_blacklist=['CameraNode', 'ScreenNode']):
    '''Reads a previously exported avango-gua scene graph from a json-file'''
    graph = avango.gua.nodes.SceneGraph(Name=name)

    # dictionary to map node ids to actual nodes
    nodes = {0: graph.Root.value}

    # load graph from json of given file name
    with open(filename, 'r') as json_file:
        for line in json_file:
            # parse json line to node
            node, id, parent_id = dict_to_node(json.loads(line))

            # restore hierarchy based on the loaded parent id
            if parent_id == -1:
                # -1 marks the root node
                pass
                # TODO: set attributes that are allowed to be written
            else:
                # store node by id
                nodes[id] = node
                # append to its parent
                nodes[parent_id].Children.value.append(node)

    return graph

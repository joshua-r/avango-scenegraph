#!/usr/bin/env python3

from collections import deque
import json

from .conversion import node_to_dict


TYPE_BLACKLIST = ['CameraNode', 'ScreenNode']


def export_scenegraph(graph, filename):
    '''Writes the given avango-gua scene graph into a json-file'''

    # counter as unique id for every node to store relations between nodes;
    # starts at one because root node is 0
    node_id = 1

    # holds tuples of node and parent-id for nodes to be stored
    queue = deque()

    # function to add tuples of the form (node, parent_id) to the queue
    def add_nodes_to_queue(nodes):
        queue.extend([(node, parent) for node, parent in nodes
                      if not type(node).__name__ in TYPE_BLACKLIST])

    # initialize queue with child nodes of the root node
    add_nodes_to_queue([(child, 0)
                        for child in graph.Root.value.Children.value])

    # store graph as json into file with of given filename
    with open(filename, 'w') as json_file:
        while len(queue):
            # retrieve current node (FIFO)
            node, parent_id = queue.popleft()

            # write node as one json-object as one line into the file
            json_file.write(
                json.dumps(
                    obj=node_to_dict(
                        node=node, id=node_id, parent_id=parent_id),
                    sort_keys=True))
            json_file.write('\n')

            # add the node's children to the queue and store the current node's
            # id as their parent-id
            add_nodes_to_queue([(child, node_id)
                                for child in node.Children.value])

            # increase the counter to assign the next node the next free id
            node_id += 1

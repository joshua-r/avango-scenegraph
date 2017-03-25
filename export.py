#!/usr/bin/env python3

from collections import deque
import json

from .conversion import node_to_dict

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

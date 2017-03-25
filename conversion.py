#!/usr/bin/env python3

import avango
import avango.gua

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
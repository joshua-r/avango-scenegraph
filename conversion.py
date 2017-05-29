#!/usr/bin/env python3

import avango
import avango.gua


def serialize_field_value(value):
    if type(value) in [str, int, float, bool]:
        return value
    elif type(value) == avango.gua.Vec3:
        return [value.x, value.y, value.z]
    elif type(value) == avango.gua.Vec4:
        return [value.x, value.y, value.z, value.w]
    elif type(value) == avango.gua.Quat:
        return [value.x, value.y, value.z, value.w]
    elif type(value) == avango.gua.Mat4:
        return mat_to_list(value)
    elif type(value) == avango.gua.Color:
        return [value.r, value.g, value.b]
    elif type(value) == avango.gua.Material:
        return {
            'Name': value.Name.value,
            'ShaderName': value.ShaderName.value,
            'EnableBackfaceCulling': value.EnableBackfaceCulling.value
        }
    elif type(value) in [avango.MFString_wrapper, avango.MFFloat_wrapper]:
        return [item for item in value]
    else:
        raise TypeError(
            'There is no conversion from type {} to a json-compatible type'
            .format(type(value).__name__))


def mat_to_list(mat):
    if type(mat) == avango.gua.Mat4:
        size = 4
    elif type(mat) == avango.gua.Mat3:
        size = 3
    else:
        raise TypeError(
            'Given matrix of type {} cannot be converted to a list!'.format(
                type(mat).__name__))

    return [
        mat.get_element(row, col) for row in range(size) for col in range(size)
    ]


def mat_from_list(l):
    if len(l) == 16:
        mat = avango.gua.Mat4()
        size = 4
    elif len(l) == 9:
        mat = avango.gua.Mat3()
        size = 3
    else:
        raise ValueError('List of length {} cannot be converted to a matrix!'.
                         format(len(l)))

    for i, value in enumerate(l):
        row = i // size
        col = i % size
        mat.set_element(row, col, value)

    return mat

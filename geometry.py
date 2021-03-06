import numpy as np


def normalize(v):
    return v / np.sqrt(np.sum(v[:3] ** 2))


def scale(factor):
    result = np.identity(4)
    result[0][0] = result[1][1] = result[2][2] = factor
    return result


def rotate(angle, axis):
    a = angle
    c = np.cos(a)
    s = np.sin(a)

    axis = normalize(axis)
    temp = np.array((1. - c) * axis)

    result = np.zeros(shape=(3, 3))
    result[0][0] = c + temp[0] * axis[0]
    result[0][1] = 0 + temp[0] * axis[1] + s * axis[2]
    result[0][2] = 0 + temp[0] * axis[2] - s * axis[1]

    result[1][0] = 0 + temp[1] * axis[0] - s * axis[2]
    result[1][1] = c + temp[1] * axis[1]
    result[1][2] = 0 + temp[1] * axis[2] + s * axis[0]

    result[2][0] = 0 + temp[2] * axis[0] + s * axis[1]
    result[2][1] = 0 + temp[2] * axis[1] - s * axis[0]
    result[2][2] = c + temp[2] * axis[2]

    return result


def look_at(eye, center, up):
    f = normalize(center - eye)
    u = normalize(up)
    s = normalize(np.cross(f, u))
    u = np.cross(s, f)
    result = np.identity(4)
    result[0][0] = s[0]
    result[1][0] = s[1]
    result[2][0] = s[2]
    result[0][1] = u[0]
    result[1][1] = u[1]
    result[2][1] = u[2]
    result[0][2] = -f[0]
    result[1][2] = -f[1]
    result[2][2] = -f[2]
    result[3][0] = -np.dot(s, eye)
    result[3][1] = -np.dot(u, eye)
    result[3][2] = np.dot(f, eye)
    return result


def get_perspective(fov_y, aspect, z_near, z_far):
    tan_half_fov_y = np.tan(fov_y / 2)
    result = np.zeros(shape=(4, 4))
    result[0][0] = 1 / (aspect * tan_half_fov_y)
    result[1][1] = 1 / tan_half_fov_y
    result[2][2] = - (z_far + z_near) / (z_far - z_near)
    result[2][3] = - 1
    result[3][2] = - (2 * z_far * z_near) / (z_far - z_near)
    return result


def perspective_divide(point):
    return np.array([
        point[0] / point[3],
        -point[1] / point[3]
    ])

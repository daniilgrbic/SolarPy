import numpy as np
import numpy.typing as npt


def direction_vector(x, y=0, z=0):
    if type(x) == list or type(x) == npt.NDArray:
        return np.array(x + [0])
    return np.array([x, y, z, 0])


def position_vector(x, y=0, z=0):
    if type(x) == list or type(x) == npt.NDArray:
        return np.array(x + [1])
    return np.array([x, y, z, 1])


def normalize(v):
    return v / np.sqrt(np.sum(v[:3] ** 2))


def look_at(eye, center, up):
    f = normalize(center - eye)
    u = normalize(up)
    s = normalize(np.cross(f, u))
    u = np.cross(s, f)
    result = np.zeros(shape=(4, 4))
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


def get_rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / np.sqrt(np.dot(axis, axis))
    a = np.cos(theta / 2.0)
    b, c, d = -axis * np.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac), 0],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab), 0],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc, 0],
                     [0, 0, 0, 1]])

"""Finite deformation calculations on a fixed tetrahedral material mesh.

All arrays use column-vector deformation gradients, x = F X + b. Stored point
arrays are rows, so contractions use explicit einsum. No infinitesimal-strain
approximation is used. Directional engineering strain and Green-Lagrange
components are deliberately distinct.
"""
import numpy as np


def edge_matrices(points, cells):
    return np.swapaxes(points[cells[:, 1:]] - points[cells[:, 0], None], -1, -2)


def deformation_gradient(reference, deformed, cells):
    return np.einsum('nij,njk->nik', edge_matrices(deformed, cells),
                     np.linalg.inv(edge_matrices(reference, cells)))


def strain(F, directions):
    C = np.einsum('nji,njk->nik', F, F)
    E = .5 * (C - np.eye(3))
    engineering, lagrange = [], []
    for e in directions:
        stretch2 = np.einsum('ni,nij,nj->n', e, C, e)
        engineering.append(np.sqrt(np.maximum(stretch2, 0)) - 1)
        lagrange.append(np.einsum('ni,nij,nj->n', e, E, e))
    return np.stack(engineering, axis=-1), np.stack(lagrange, axis=-1), np.linalg.det(F)


def boundary(cells):
    faces = np.concatenate([cells[:, k] for k in [[1, 2, 3], [0, 3, 2], [0, 1, 3], [0, 2, 1]]])
    owners = np.tile(np.arange(len(cells)), 4)
    _, idx, count = np.unique(np.sort(faces, axis=1), axis=0, return_index=True, return_counts=True)
    idx = idx[count == 1]
    return faces[idx], owners[idx]


def rigid_fit(source, target):
    xs, xt = source - source.mean(0), target - target.mean(0)
    u, _, vt = np.linalg.svd(np.einsum('ni,nj->ij', xs, xt))
    R = np.einsum('ij,jk->ik', u, vt)
    if np.linalg.det(R) < 0:
        u[:, -1] *= -1
        R = np.einsum('ij,jk->ik', u, vt)
    offset = target.mean(0) - np.einsum('j,jk->k', source.mean(0), R)
    fitted = np.einsum('nj,jk->nk', source, R) + offset
    return R, offset, np.linalg.norm(fitted-target, axis=1)


def normalize(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def cell_directions(point_data, cells):
    # The source has no anatomical directions for AHA 0 (RV/unassigned).
    # Mask these regions at use sites, rather than filling in arbitrary axes.
    radial = normalize(point_data['rads'][cells].mean(1))
    longitudinal = point_data['longs'][cells].mean(1)
    longitudinal -= np.einsum('ni,ni->n', longitudinal, radial)[:, None] * radial
    longitudinal = normalize(longitudinal)
    circumferential = normalize(np.cross(longitudinal, radial))
    return np.array([longitudinal, circumferential, radial])


def nodal_average(values, cells, weights, count):
    weighted = values * weights[:, None] if values.ndim == 2 else values * weights
    result = np.zeros((count, *values.shape[1:]))
    denom = np.zeros(count)
    for j in range(4):
        np.add.at(result, cells[:, j], weighted)
        np.add.at(denom, cells[:, j], weights)
    return result / np.maximum(denom.reshape((-1,)+(1,)*(values.ndim-1)), 1e-15)


def calculation_tests():
    X = np.array([[0., 0., 0.], [2., 0., 0.], [0., 3., 0.], [0., 0., 4.]])
    cells = np.array([[0, 1, 2, 3]])
    dirs = np.eye(3)[:, None, :]
    errors = {}
    theta = .81
    R = np.array([[np.cos(theta), -np.sin(theta), 0], [np.sin(theta), np.cos(theta), 0], [0, 0, 1.]])
    F = deformation_gradient(X, np.einsum('ij,nj->ni', R, X)+[13, -5, 8], cells)
    eng, E, J = strain(F, dirs)
    errors['rigid_strain_max_abs'] = float(max(abs(eng).max(), abs(E).max()))
    errors['rigid_J_error'] = float(abs(J-1).max())
    A = np.diag([.8, .9, 1/(.8*.9)])
    F = deformation_gradient(X, np.einsum('ij,nj->ni', A, X), cells)
    eng, E, J = strain(F, dirs)
    errors['affine_engineering_error'] = float(abs(eng[0]-(np.diag(A)-1)).max())
    errors['affine_green_lagrange_error'] = float(abs(E[0]-(np.diag(A)**2-1)/2).max())
    errors['volume_preserving_J_error'] = float(abs(J-1).max())
    errors['identity_gradient_error'] = float(abs(deformation_gradient(X, X, cells)-np.eye(3)).max())
    # Objectivity: superposed rotation does not change the strain tensor.
    F2 = np.einsum('ij,njk->nik', R, F)
    eng2, E2, _ = strain(F2, dirs)
    errors['superposed_rotation_strain_error'] = float(max(abs(eng-eng2).max(), abs(E-E2).max()))
    assert max(errors.values()) < 1e-12, errors
    return errors

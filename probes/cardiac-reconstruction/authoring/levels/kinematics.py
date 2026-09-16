"""Independent scorer: solve reference edge systems, never use author inverse code."""
import numpy as np


def fields(reference, points, tetra, directions, labels):
    edges0 = reference[tetra[:, 1:]] - reference[tetra[:, :1]]
    edges = points[:, tetra[:, 1:]] - points[:, tetra[:, :1]]
    # Edge matrices here store edges in ROWS; solve D0 @ F.T = Dt.
    F = np.linalg.solve(edges0[None], edges).swapaxes(-1, -2)
    E = (F.swapaxes(-1, -2) @ F - np.eye(3)) / 2
    J = np.linalg.det(edges) / np.linalg.det(edges0)[None]
    valid = (labels > 0) & np.all(np.linalg.norm(directions, axis=-1) > .99, axis=0)
    transformed = np.einsum('tmij,dmj->tmdi', F, directions)
    engineering = np.linalg.norm(transformed, axis=-1) - 1
    engineering[:, ~valid] = np.nan
    return dict(F=F, E=E, J=J, engineering=engineering, valid=valid)


def analytic_inputs():
    X = np.array([[0.,0.,0.],[2.,0.,0.],[0.,3.,0.],[0.,0.,4.],
                  [10.,0.,0.],[12.,0.,0.],[10.,3.,0.],[10.,0.,4.]])
    tetra = np.array([[0,1,2,3],[4,5,6,7]])
    axes = np.repeat(np.eye(3)[:,None,:], 2, axis=1)
    axes[:,1] = 0
    theta = .73
    R = np.array([[np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1]])
    A = np.array([[.78,.21,0],[0,.91,.13],[0,0,1.22]])
    points = np.array([X, X@R.T+[4,-3,2], X@A.T+[1,2,3], X@(R@A).T+[5,8,-2]])
    return dict(reference_points=X, points=points, tetra=tetra, directions=axes,
                cell_labels=np.array([1,2]))


def from_input(data):
    return fields(data['reference_points'], data['points'], data['tetra'],
                  data['directions'], data['cell_labels'])

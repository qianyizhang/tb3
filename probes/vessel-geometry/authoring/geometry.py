"""Physical-space vessel geometry. Arrays are XYZ; all public points are RAS mm."""
import heapq
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree


def transform(points, affine):
    return np.einsum('...j,ij->...i', np.asarray(points), affine[:3, :3]) + affine[:3, 3]


def sample(array, affine, points, order=1, cval=-1024.):
    ijk = transform(points, np.linalg.inv(affine))
    return ndi.map_coordinates(np.asarray(array, dtype=np.float32),
                               np.moveaxis(ijk, -1, 0), order=order,
                               mode='constant', cval=cval, prefilter=False)


def read_centerline(path):
    from vtkmodules.vtkIOLegacy import vtkPolyDataReader
    from vtkmodules.util.numpy_support import vtk_to_numpy
    r = vtkPolyDataReader(); r.SetFileName(str(path))
    r.ReadAllScalarsOn(); r.ReadAllFieldsOn(); r.Update()
    p = r.GetOutput()
    xyz = vtk_to_numpy(p.GetPoints().GetData()).astype(float) * [-1, -1, 1]
    pd = p.GetPointData()
    fields = {pd.GetArray(i).GetName(): vtk_to_numpy(pd.GetArray(i))
              for i in range(pd.GetNumberOfArrays()) if pd.GetArray(i) is not None}
    packed = vtk_to_numpy(p.GetLines().GetData()); lines = []; k = 0
    while k < len(packed):
        n = int(packed[k]); lines.append(packed[k+1:k+n+1].astype(int)); k += n+1
    if not lines: raise ValueError('Centerline has no line connectivity')
    return xyz, fields, lines


def named_route(xyz, fields, lines, label):
    """Walk released line connectivity from ostium to a named branch endpoint."""
    graph = {i: {} for i in range(len(xyz))}
    for line in lines:
        for i, j in zip(line[:-1], line[1:]):
            d = float(np.linalg.norm(xyz[i]-xyz[j])); graph[i][j] = d; graph[j][i] = d
    # Branch cells can repeat a junction using a different point ID.
    for i, j in cKDTree(xyz).query_pairs(1e-5): graph[i][j] = graph[j][i] = 0.
    starts = np.flatnonzero(fields['start_points'])
    ends = np.flatnonzero((fields['end_points'] != 0) & (fields['segment_label'] == label) & (fields['start_points'] == 0))
    if len(starts) != 1 or not len(ends):
        raise ValueError(f'Ambiguous root or missing named end: {starts}, {ends}')
    start = int(starts[0]); dist = np.full(len(xyz), np.inf); dist[start] = 0
    prev = np.full(len(xyz), -1); q = [(0., start)]
    while q:
        d, i = heapq.heappop(q)
        if d != dist[i]: continue
        for j, step in graph[i].items():
            if d+step < dist[j]:
                dist[j] = d+step; prev[j] = i; heapq.heappush(q, (d+step, j))
    end = int(ends[np.argmax(dist[ends])])
    if not np.isfinite(dist[end]): raise ValueError('Disconnected reference route')
    ids = [end]
    while ids[-1] != start: ids.append(int(prev[ids[-1]]))
    ids = np.array(ids[::-1]); return xyz[ids], ids


def resample_path(points, step=.5, smooth_mm=.6):
    p = np.asarray(points, dtype=float)
    p = p[np.r_[True, np.linalg.norm(np.diff(p, axis=0), axis=1) > 1e-7]]
    s = np.r_[0., np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    if len(p) < 2 or not s[-1] > 0: raise ValueError('Degenerate path')
    grid = np.linspace(0, s[-1], int(np.ceil(s[-1]/step))+1)
    q = np.column_stack([np.interp(grid, s, p[:, j]) for j in range(3)])
    if smooth_mm:
        q = ndi.gaussian_filter1d(q, smooth_mm/(grid[1]-grid[0]), axis=0, mode='nearest')
        q[0] = p[0]; q[-1] = p[-1]
        return resample_path(q, step, 0.)
    return q, grid


def frames(points):
    """Parallel transport; initial normal = projected least-aligned RAS axis."""
    p = np.asarray(points); t = np.gradient(p, axis=0)
    norm = np.linalg.norm(t, axis=1)
    if np.min(norm) < 1e-9: raise ValueError('Zero tangent')
    t /= norm[:, None]; n = np.empty_like(t)
    axis = np.eye(3)[np.argmin(np.abs(t[0]))]
    n[0] = axis - np.dot(axis, t[0])*t[0]; n[0] /= np.linalg.norm(n[0])
    for i in range(1, len(p)):
        v = np.cross(t[i-1], t[i]); c = np.dot(t[i-1], t[i])
        if c < -.99: raise ValueError('Reversing path cannot define a stable frame')
        n[i] = n[i-1] + np.cross(v, n[i-1]) + np.cross(v, np.cross(v, n[i-1]))/(1+c)
        n[i] -= np.dot(n[i], t[i])*t[i]; n[i] /= np.linalg.norm(n[i])
    return t, n, np.cross(t, n)


def cpr_coordinates(points, normal, binormal, angles_deg, offsets_mm):
    a = np.deg2rad(angles_deg)
    directions = np.cos(a)[:, None, None]*normal + np.sin(a)[:, None, None]*binormal
    return points[None, :, None, :] + directions[:, :, None, :]*np.asarray(offsets_mm)[None, None, :, None]


def section_coordinates(points, normal, binormal, offsets_mm):
    u, v = np.meshgrid(offsets_mm, offsets_mm, indexing='ij')
    return points[:, None, None, :] + normal[:, None, None, :]*u[None, :, :, None] + binormal[:, None, None, :]*v[None, :, :, None]


def mesh_from_mask(mask, affine, step_size=1):
    from skimage.measure import marching_cubes
    import trimesh
    # Padding explicitly caps source mask termini, including crop faces.
    vertices, faces, _, _ = marching_cubes(np.pad(mask.astype(np.uint8), 1), .5, step_size=step_size)
    mesh = trimesh.Trimesh(transform(vertices-1, affine), faces, process=False)
    mesh.fix_normals(multibody=True)
    return mesh


def runs_of_false(values):
    b = np.r_[False, ~np.asarray(values, dtype=bool), False]
    edges = np.flatnonzero(b[1:] != b[:-1])
    return list(zip(edges[::2].tolist(), edges[1::2].tolist()))

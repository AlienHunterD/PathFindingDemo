# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 15:24:48 2025

@author: histo
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from pathlib import Path as _Path
from datetime import datetime
import secrets

# ---------------------- Parameters ----------------------
num_points = 12
width, height = 500, 300

# <<< change number of clusters & size here >>>
num_clusters = 5          # how many clusters of inner points
pts_per_cluster = 5       # points per cluster
cluster_std_px = 19      # cluster spread (std dev in pixels)
margin_from_edge = 4      # keep inner points a bit away from polygon edge
close_cluster_loops = True  # connect last->first inside each cluster
# --------------------------------------------------------

# --------- save helpers ----------
def make_unique_filename(base="shape", ext=".txt", out_dir="exports", suffix=None):
    """
    Returns a unique path like: exports/shape_2025-08-13_14-22-05_ab12cd.txt
    """
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    tag = secrets.token_hex(3)  # 6 hex chars
    stem = f"{base}_{ts}_{tag}"
    if suffix:
        stem += f"_{suffix}"
    out = _Path(out_dir) / f"{stem}{ext}"
    out.parent.mkdir(parents=True, exist_ok=True)
    return out

def save_vertices_txt(path, outer_ccw, clusters_ccw, centers=None):
    p = _Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        f.write("OUTER\n")
        for x, y in outer_ccw:
            f.write(f"{int(x)}, {int(y)}\n")
        for i, cl in enumerate(clusters_ccw):
            f.write(f"\nCLUSTER {i}\n")
            for x, y in cl:
                f.write(f"{int(x)}, {int(y)}\n")
        if centers is not None:
            f.write("\nCENTERS\n")
            for i, (x, y) in enumerate(centers):
                f.write(f"{i}: {int(x)}, {int(y)}\n")
    return p

# Generate random integer outer points
points = np.random.randint(0, [width, height], size=(num_points, 2))

# CCW order by angle around centroid
centroid = np.mean(points, axis=0)
angles = np.arctan2(points[:, 1] - centroid[1], points[:, 0] - centroid[0])
points_ccw = points[np.argsort(angles)]

# --- helper: sample K integer points inside polygon ---
def sample_points_inside_polygon(poly_xy, k, margin=0, rng=None):
    poly = np.asarray(poly_xy, dtype=float)
    path = Path(poly)
    minx, miny = poly.min(axis=0)
    maxx, maxy = poly.max(axis=0)
    minx = int(np.ceil(minx + margin)); miny = int(np.ceil(miny + margin))
    maxx = int(np.floor(maxx - margin)); maxy = int(np.floor(maxy - margin))
    if rng is None: rng = np.random.default_rng()

    inside = []
    seen = set()
    while len(inside) < k:
        batch_n = max(1024, 4 * (k - len(inside)))
        cand = np.column_stack([
            rng.integers(minx, maxx + 1, size=batch_n),
            rng.integers(miny, maxy + 1, size=batch_n)
        ])
        mask = path.contains_points(cand + 0.0, radius=-margin)
        take = cand[mask]
        for p in take:
            tp = (int(p[0]), int(p[1]))
            if tp not in seen:
                inside.append(tp)
                seen.add(tp)
                if len(inside) >= k:
                    break
    return np.array(inside, dtype=int)

# --- helper: sample N cluster centers inside polygon ---
def sample_cluster_centers(poly_xy, n_centers, margin=5, rng=None):
    return sample_points_inside_polygon(poly_xy, n_centers, margin=margin, rng=rng)

# --- helper: sample points around centers but keep them inside polygon ---
def sample_cluster_points(poly_xy, centers, pts_per, std_px=20, margin=1, rng=None):
    poly = np.asarray(poly_xy, dtype=float)
    path = Path(poly)
    if rng is None: rng = np.random.default_rng()
    clusters = []
    for c in centers:
        cx, cy = c
        pts = []
        seen = set()
        while len(pts) < pts_per:
            batch = rng.normal(loc=[cx, cy], scale=[std_px, std_px],
                               size=(max(64, 4*(pts_per-len(pts))), 2))
            batch = np.clip(batch, [0,0], [width, height])  # keep in canvas
            cand = np.rint(batch).astype(int)               # integer grid
            mask = path.contains_points(cand + 0.0, radius=-margin)
            cand = cand[mask]
            for p in cand:
                tp = (int(p[0]), int(p[1]))
                if tp not in seen:
                    pts.append(tp); seen.add(tp)
                    if len(pts) >= pts_per:
                        break
        clusters.append(np.array(pts, dtype=int))
    return clusters

# --- helper: order cluster points CCW around cluster centroid ---
def order_ccw(points_int):
    pts = np.asarray(points_int, dtype=float)
    center = pts.mean(axis=0)
    ang = np.arctan2(pts[:,1] - center[1], pts[:,0] - center[0])
    return np.asarray(points_int)[np.argsort(ang)]

# --------- build clusters inside your outer polygon ----------
rng = np.random.default_rng()
centers = sample_cluster_centers(points_ccw, num_clusters, margin=10, rng=rng)
clusters = sample_cluster_points(points_ccw, centers, pts_per_cluster,
                                 std_px=cluster_std_px, margin=margin_from_edge, rng=rng)

# Order each cluster CCW (so when you connect, they’re neat loops/paths)
clusters_ccw = [order_ccw(cl) for cl in clusters]

# --- plotting wrapped so we can save the same figure later ---
def draw_plot(outer_ccw, clusters_ccw, centers=None, title="Outer polygon with clustered inner integer points"):
    fig = plt.figure(figsize=(9, 5))

    # connect outer in order and close
    xs = np.r_[outer_ccw[:, 0], outer_ccw[0, 0]]
    ys = np.r_[outer_ccw[:, 1], outer_ccw[0, 1]]
    plt.plot(xs, ys, '-k', linewidth=2, zorder=3, label='outer polygon')

    # outer vertices
    plt.scatter(outer_ccw[:, 0], outer_ccw[:, 1], color='red', zorder=4, label='outer verts')
    for i, (x, y) in enumerate(outer_ccw):
        plt.text(x + 5, y + 5, str(i), fontsize=8, color='blue')

    # clusters: different color per cluster
    colors = plt.rcParams['axes.prop_cycle'].by_key().get('color', ['tab:green','tab:orange','tab:purple','tab:cyan'])
    for ci, cl in enumerate(clusters_ccw):
        col = colors[ci % len(colors)]
        plt.scatter(cl[:,0], cl[:,1], s=30, color=col, zorder=5, label=f'cluster {ci}')
        if len(cl) >= 2:
            xs = np.r_[cl[:,0], cl[0,0]] if close_cluster_loops else cl[:,0]
            ys = np.r_[cl[:,1], cl[0,1]] if close_cluster_loops else cl[:,1]
            plt.plot(xs, ys, '-', lw=1.8, color=col, zorder=4)
        # no X marker for centers by default
        # if centers is not None: plt.plot(centers[ci,0], centers[ci,1], 'x', color=col)

    plt.title(title)
    plt.xlim(0, width); plt.ylim(0, height)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True, linestyle=':')
    plt.legend(ncol=2)
    plt.tight_layout()
    return fig

# --- draw & show first ---
fig = draw_plot(points_ccw, clusters_ccw, centers=centers)
plt.show()

# --- prompt to optionally save BOTH vertices (.txt) and plot (.png) ---
choice = input("Save this shape's vertices AND the plot? (y/n): ").strip().lower()
if choice == "y":
    txt_path = make_unique_filename(base="shape_vertices", ext=".txt", out_dir="exports")
    img_path = make_unique_filename(base="shape_plot",     ext=".png", out_dir="exports")

    save_vertices_txt(txt_path, points_ccw, clusters_ccw, centers=centers)
    # save the same figure you just saw
    fig.savefig(img_path, dpi=300, bbox_inches="tight")
    print(f"Saved vertices to: {txt_path}")
    print(f"Saved plot to:     {img_path}")
else:
    print("Not saved. You can generate another shape immediately.")

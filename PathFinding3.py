# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 11:53:11 2025

@author: dbied
"""
import math
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, LineString
import numpy as np

def cast_rays_with_holes(polygon, viewpoint, n_rays=500):
    ray_points = []
    #angles = np.linspace(0, 2 * np.pi, n_rays)

    # Extract exterior and holes
    edges = []
    coords = list(polygon.exterior.coords)
    edges.extend(zip(coords[:-1], coords[1:]))

    for interior in polygon.interiors:
        coords = list(interior.coords)
        edges.extend(zip(coords[:-1], coords[1:]))
    
    boundary_verts = list(polygon.exterior.coords)
    interior_verts = []
    for item in [list(interior.coords) for interior in polygon.interiors]:
        interior_verts += item
    
    vertices = boundary_verts + interior_verts

    angles = []
    ox, oy = viewpoint
    for vx,vy in vertices:
        dx = vx - ox
        dy = vy - oy
        angles.append(math.atan2(dy, dx))
    angles.sort()

    for angle in angles:
        dx, dy = np.cos(angle), np.sin(angle)
        far_point = (viewpoint[0] + dx * 1000, viewpoint[1] + dy * 1000)
        ray = LineString([viewpoint, far_point])
        min_dist = float('inf')
        closest_pt = None
        for seg_start, seg_end in edges:
            edge = LineString([seg_start, seg_end])
            if ray.intersects(edge):
                pt = ray.intersection(edge)
                print(pt.x, pt.y)
                if isinstance(pt, Point) and (pt.x,pt.y) not in interior_verts:
                    dist = Point(viewpoint).distance(pt)
                    if dist < min_dist:
                        min_dist = dist
                        closest_pt = pt
        if closest_pt:
            ray_points.append((closest_pt.x, closest_pt.y))
    return ray_points

# Define outer polygon and hole
outer = [(0,0), (10,0), (10,10), (0,10)]
holes = [[(3,3), (5,3), (5,5), (3,5)]]

polygon = Polygon(outer, holes)
viewpoint = (1,2)
destination = [7, 6]

# Compute visibility
vis_points = cast_rays_with_holes(polygon, viewpoint)
vis_polygon = Polygon(vis_points)

# Plotting
fig, ax = plt.subplots()
ox, oy = zip(*polygon.exterior.coords)
ax.plot(ox, oy, 'k-', label='Outer Boundary')

for interior in polygon.interiors:
    hx, hy = zip(*interior.coords)
    ax.plot(hx, hy, 'k-', label='Hole')
    ax.plot(hx, hy, 'b.', label='Vertices')    

vx, vy = zip(*vis_polygon.exterior.coords)
ax.fill(vx, vy, color='skyblue', alpha=0.5, label='Visibility')

ax.plot(*viewpoint, 'ro', label='Viewpoint')
ax.plot(destination[0], destination[1], 'go')
ax.set_aspect('equal')
plt.title("Visibility Polygon with Holes")
#plt.legend()
plt.show()
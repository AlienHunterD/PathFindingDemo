# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 12:59:09 2025

@author: dbied
"""

import triangle
import matplotlib.pyplot as plt

verts = [[0, 0], [10, 0], [10, 10], [0, 10], [3,3], [5,3], [5,5], [3,5],
        [2,6], [3,6], [3,7], [2,7]]

segs = [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [8, 9],
        [9, 10], [10, 11], [11, 8]]   # hole

start = [3,2]
destination = [7, 6]

# Define polygon with a hole
A = dict(vertices=verts, segments=segs)  # point inside the hole

# Triangulate
B = triangle.triangulate(A, 'p')

# Manual plotting
fig, ax = plt.subplots()
vertices = B['vertices']
segments = B['segments']
triangles = B['triangles']

for line in segments:
    pts = [vertices[x] for x in line]
    xs,ys = zip(*pts)
    ax.plot(xs, ys, 'k-')

for tri in triangles:
    pts = [vertices[i] for i in tri] + [vertices[tri[0]]]  # close triangle
    xs, ys = zip(*pts)
    ax.plot(xs, ys, 'k:',linewidth=0.5)

ax.plot(vertices[:, 0], vertices[:, 1], 'bo', markersize=3)
ax.plot(start[0], start[1], 'ro', markersize=3)
ax.plot(destination[0], destination[1], 'go', markersize=3)


ax.set_aspect('equal')
plt.title("Plot of Triangulated Polygon")
plt.show()


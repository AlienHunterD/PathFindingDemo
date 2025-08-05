# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 11:53:11 2025

@author: dbied
"""

import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, LineString
import numpy as np
import random

NUM_POINTS = 10
WIDTH = 10
HEIGHT = 10

def point_in_obstacles(point, obstacles):
    for obs in obstacles:
        if obs.contains(point):
            return True
    return False

def point_on_obstacles(point, obstacles):
    for obs in obstacles:
        if obs.touches(point):
            return True   
    return False

def filter_points(points, obstacles, boundary):
    result = []
    for point in points:
        pt = Point(point[0], point[1])
        if point_in_obstacles(pt, obstacles):
            continue
        if point_on_obstacles(pt, obstacles):
            continue
        if point_on_obstacles(pt, boundary):
            continue
        result.append(point)
    
    return result


def is_visible(p1, p2, obstacles):
    """Check if the line between p1 and p2 intersects any obstacle."""
    line = LineString([p1, p2])
    for obs in obstacles:
        if line.crosses(obs):
            return False
    return True

def compute_visibility_triangles(start, boundary, obstacles):
    """Compute visibility polygon from a start point within a region with obstacles."""
    all_points = list(boundary.exterior.coords)
    for obs in obstacles:
        all_points.extend(obs.exterior.coords)

    visible_points = []
    for pt in all_points:
        if pt == start:
            continue
        if is_visible(start, pt, obstacles + [boundary]):
            visible_points.append(pt)

    # Sort points by angle to form a polygon
    visible_points.sort(key=lambda p: np.arctan2(p[1] - start[1], p[0] - start[0]))
    
    results = [Polygon([start, visible_points[0], visible_points[-1]])]
    for index in range(len(visible_points) - 1):
        results.append(Polygon([start] + visible_points[index:index+2]))
    
    return results


# Define the boundary of the region
boundary = Polygon([(0, 0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT)])

# Define polygonal obstacles
"""obstacles = [
    Polygon([(2, 2), (9, 2), (9, 3), (3, 3), (3, 7), (9, 7), (9, 8), (2, 8)]),
    Polygon([(6.5, 4), (7, 4), (7, 6), (6.5, 6)]),
]"""
    
obstacles = [
    Polygon([(2, 6), (3, 6), (3, 9), (7, 9), (7, 6), (8, 6), (8, 10), (2, 10)]),
    Polygon([(2, 0), (8, 0), (8, 1), (3, 1), (3, 4), (2, 4)]),
    Polygon([(4.5, 3), (8, 3), (8, 4), (5.5, 4), (5.5, 7), (4.5, 7)])
]
    
    
# Define the starting point
start_point = (1, 5)


points = [(WIDTH*x/NUM_POINTS,HEIGHT*y/NUM_POINTS) for x in range(0,NUM_POINTS+1) for y in range(0,NUM_POINTS+1)]
points = filter_points(points, obstacles, [boundary])

visibility_points = {x:0 for x in points}

working_group = [] # Group of points at the current stage

for point,value in visibility_points.items():
    if is_visible(point, start_point, obstacles):
        visibility_points[point] = 1
        working_group.append(point)

new_group = []        
for point,value in visibility_points.items():
    if value == 0: #Not visited
        for back_point in working_group:
            if is_visible(point, back_point, obstacles):
                visibility_points[point] = 2
                new_group.append(point)

working_group = [] # Group of points at the current stage
for point,value in visibility_points.items():
    if value == 0: #Not visited
        for back_point in new_group:
            if is_visible(point, back_point, obstacles):
                visibility_points[point] = 3
                working_group.append(point)


for point,value in visibility_points.items():
    if value == 0: #Not visited
        for back_point in working_group:
            if is_visible(point, back_point, obstacles):
                visibility_points[point] = 4


# Compute the visibility polygon
#visibility_triangles = compute_visibility_triangles(start_point, boundary, obstacles)

# Plotting
fig, ax = plt.subplots()
x, y = boundary.exterior.xy
ax.plot(x, y, 'black')

for obs in obstacles:
    x, y = obs.exterior.xy
    ax.fill(x, y, 'gray')

color_options = ["magenta", "blue", "orange", "green", "purple", "teal"]

"""for item in visibility_triangles:
    vx, vy = item.exterior.xy
    ax.fill(vx, vy, "yellow", alpha=0.5, label='Visibility Polygon')
"""
    
for point,value in visibility_points.items():
    ax.plot(point[0], point[1], marker='o', markersize=1, color = color_options[value])

ax.plot(*start_point, 'ro', label='Start Point')
ax.set_aspect('equal')
#ax.legend()
plt.title("Visibility Polygon using Lee's Visibility Graph Algorithm")
plt.show()

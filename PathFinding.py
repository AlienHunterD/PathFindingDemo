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
    angles = []
    
    # Extract exterior and holes
    edges = []
    coords = list(polygon.exterior.coords)
    edges.extend(zip(coords[:-1], coords[1:]))
    
    all_vertices = coords

    for interior in polygon.interiors:
        coords = list(interior.coords)
        all_vertices += coords
        edges.extend(zip(coords[:-1], coords[1:]))

    #print(all_vertices)
    
    for vx, vy in all_vertices:
        temp = math.atan2(vy - viewpoint[1], vx - viewpoint[0])
        #print(temp)
        angles.append(temp + 0.00001)
        angles.append(temp)
        angles.append(temp - 0.00001)
    
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
                if isinstance(pt, Point):
                    dist = Point(viewpoint).distance(pt)
                    if dist < min_dist:
                        min_dist = dist
                        closest_pt = pt
        if closest_pt:
            #ray_points.append((closest_pt.x, closest_pt.y))
            ray_points.append((round(closest_pt.x, 3), round(closest_pt.y, 3)))
            
    return ray_points

def is_window(polygon, point1, point2):
    """ Points 1 and 2 are an edge on the visibilty polygon and we would like to 
    know if they are a window, or if they are on the edge of a boundry or hole """
    
    if math.hypot(point1[0]-point2[0], point1[1]-point2[1]) < 0.0001:
        return False

    
    boundary_coords = list(polygon.exterior.coords)
    edges = [LineString([boundary_coords[i], boundary_coords[i+1]]) for i in range(len(boundary_coords) - 1)]
    
    
    for interior in list(polygon.interiors):
        pts = list(interior.coords)
        edges += [LineString([pts[i], pts[i+1]]) for i in range(len(pts) - 1)]
    
    line1 = LineString([point1, point2])
    for boundary_line in edges:
        if boundary_line.intersects(line1) and boundary_line.intersection(line1).geom_type == 'LineString':
            return False
    
    return True
    
def compute_next_visibility(unvisited_polygon, windows):
    """ This function takes in an unvisited polygon and a list of windows and 
    retruns a list of new windows and the remaining un-visited region."""
    
    visited_polygon = Polygon() # newly visible region (nothing yet!)
    
    # Loop over all the windows and add to a newly visible region by projecting
    # from the end points (and lines) into the unvisited polygon
    # Compute the union of a polygon region with the current visible region
    
    # Compare the line segments that make up the currently visible polygon to
    # the line segments in the previously unvisited polygon and find the windows
    
    
    

    still_unvisited_polygon = unvisited_polygon - visited_polygon
    # return the still unvisited polygon
    # return the newly visited polygon
    
    
    
    


# Define outer polygon and hole
outer = [(0,0), (10,0), (10,10), (0,10)]
holes = [[(4,2), (6,4), (4,6), (2,4)],
        [(2,6), (3,6), (3,7), (2,7)]]

polygon = Polygon(outer, holes)
viewpoint = (1,3.5)
destination = [7, 6]

# Compute visibility
vis_points = cast_rays_with_holes(polygon, viewpoint)
vis_polygon = Polygon(vis_points)

unvisited_polygon = polygon - vis_polygon

#Find all the windows for the next step
windows = []
for i in range(len(vis_points)):
    point1 = vis_points[i]
    point2 = vis_points[(i+1)%len(vis_points)]
    if is_window(polygon, point1, point2):
        windows.append([point1, point2])


for item in windows:
    print(item)
    

# Plotting
fig, ax = plt.subplots()
ox, oy = zip(*polygon.exterior.coords)
ax.plot(ox, oy, 'k-', label='Outer Boundary')

for interior in polygon.interiors:
    hx, hy = zip(*interior.coords)
    ax.plot(hx, hy, 'k-', label='Hole')
    ax.plot(hx, hy, 'b.', label='Vertices')    

vx, vy = zip(*vis_polygon.exterior.coords)
ax.plot(vx,vy, 'g.')
ax.fill(vx, vy, color='skyblue', alpha=0.5, label='Visibility')

for item in windows:
    px,py = zip(*item)
    ax.plot(px, py, "m-")

ax.plot(*viewpoint, 'ro', label='Viewpoint')
ax.plot(destination[0], destination[1], 'go')
ax.set_aspect('equal')
plt.title("Visibility Polygon with Holes")
#plt.legend()
plt.show()
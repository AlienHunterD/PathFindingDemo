# -*- coding: utf-8 -*-
"""
A Demonstration of min-link pathfinding algorithm.

@author: dbied
"""

import triangle
import math
import heapq
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
from matplotlib.animation import PillowWriter
import numpy as np
from collections import defaultdict
from shapely.geometry import Point, Polygon, LineString, MultiLineString, MultiPolygon
from shapely.ops import unary_union

TOLERANCE = 0.001

def cast_rays_with_holes(polygon, viewpoint):
    ray_points = []
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
        angles.append(temp + 0.000001)
        angles.append(temp)
        angles.append(temp - 0.000001)
    
    angles.sort()

    for angle in angles:
        dx, dy = np.cos(angle), np.sin(angle)
        far_point = (viewpoint[0] + dx * 1000, viewpoint[1] + dy * 1000)
        near_point = (viewpoint[0] + dx * 0.01, viewpoint[1] + dy * 0.01)
        if not polygon.contains(Point(near_point)): # Fix the problem where you are along a boundary
            ray_points.append(viewpoint) 
        else:
            ray = LineString([near_point, far_point])
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
        return False # Too short a segment to be a real window

    
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

def get_windows(polygon, vis_polygon):
    """Find the newly created edges as they represent the visibility windows."""
    vis_coords= list(vis_polygon.exterior.coords)

    # Create a list of LineStrings for each segment
    vis_segments = [LineString(vis_coords[i:i+2]) for i in range(len(vis_coords) - 1)]
    poly_coords = list(polygon.exterior.coords)
    poly_segments = [LineString(poly_coords[i:i+2]) for i in range(len(poly_coords) - 1)]
    for interior in list(polygon.interiors):
        pts = list(interior.coords)
        poly_segments += [LineString([pts[i], pts[i+1]]) for i in range(len(pts) - 1)]
    
    multi_line_vis = unary_union(vis_segments)
    new_vision_poly = unary_union(poly_segments)
    
    buffered_polygon = new_vision_poly.buffer(TOLERANCE) #Grow a bit to remove more from the polygon
    
    result = multi_line_vis.difference(buffered_polygon)
    
    if result.geom_type == 'LineString': # Convert to a MultiLineString 
        result = MultiLineString([result])

    return result

def find_group(segment, polygons):
    group = -1
    start = segment[0]
    finish = segment[1]
    begin = [0,0]
    end = [0,0]
    ds = float('inf')
    de = float('inf')
    for index, poly in enumerate(polygons.geoms):
        for point in poly.exterior.coords:
            dx = point[0] - start[0]
            dy = point[1] - start[1]
            dist = dx**2 + dy**2
            if dist < ds:
                ds = dist
                group = index
                begin = point
            dx = point[0] - finish[0]
            dy = point[1] - finish[1]
            dist = dx**2 + dy**2
            if dist < de:
                de = dist
                group = index
                end = point
    return group, [begin, end]

def dijkstra(graph, start_node):
    """
    Finds the shortest paths from a start_node to all other nodes in a graph.

    Args:
        graph (dict): A dictionary representing the graph where keys are nodes
                      and values are dictionaries of neighbors and their edge weights.
                      Example: {'A': {'B': 1, 'C': 4}, 'B': {'A': 1, 'C': 2, 'D': 5}}
        start_node: The starting node for finding shortest paths.

    Returns:
        dict: A dictionary where keys are nodes and values are their shortest distances
              from the start_node. Returns float('inf') for unreachable nodes.
    """
    distances = {node: float('inf') for node in graph}
    distances[start_node] = 0
    priority_queue = [(0, start_node)]  # (distance, node)

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # If we've already found a shorter path to this node, skip
        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances



# ***** Set up the current problem and load the boundary and hole information *****
# Define outer polygon and hole
#outer = [(0,0), (10,0), (10,10), (0,10)]
#holes = [[(4,2), (6,4), (4,6), (2,4)], [(2,6), (3,6), (3,7), (2,7)]]

outer = [[0.29155672823219003, 4.823218997361478],
 [3.0356200527704487, 2.5013192612137205],
 [4.671503957783641, 4.559366754617415],
 [8.127968337730872, 2.9762532981530345],
 [9.5, 7.356200527704486],
 [6.967018469656993, 8.04221635883905],
 [6.281002638522428, 7.118733509234828],
 [8.339050131926122, 6.643799472295514],
 [6.729551451187335, 4.823218997361478],
 [3.088390501319261, 7.118733509234828],
 [4.882585751978892, 8.04221635883905],
 [2.112137203166227, 8.04221635883905],
 [1.9010554089709761, 6.643799472295514],
 [3.9591029023746707, 5.271767810026385],
 [2.824538258575198, 4.137203166226913],
 [1.6899736147757256, 4.823218997361478],
 [2.587071240105541, 5.509234828496043]]
holes = []

"""
outer =[[0.4035874439461883, 0.3139013452914798],
 [4.992526158445441, 0.25411061285500747],
 [5.9790732436472345, 1.210762331838565],
 [6.9207772795216735, 0.25411061285500747],
 [9.985052316890881, 0.25411061285500747],
 [8.04185351270553, 2.301943198804185],
 [10.0, 4.28998505231689],
 [6.9207772795216735, 4.304932735426009],
 [5.93423019431988, 3.363228699551569],
 [4.992526158445441, 4.304932735426009],
 [4.394618834080717, 4.304932735426009]]

holes = [[[6.606875934230194, 1.71898355754858],
  [7.817638266068759, 1.7339312406576979],
  [7.832585949177877, 1.7040358744394617],
  [7.4140508221225705, 1.3303437967115097],
  [6.9805680119581455, 1.3452914798206277]],
 [[5.85949177877429, 2.301943198804185],
  [4.409566517189835, 0.8221225710014947],
  [3.0642750373692076, 0.8221225710014947],
  [4.484304932735426, 2.227204783258595],
  [4.499252615844544, 2.316890881913303],
  [4.0807174887892375, 2.7503736920777277],
  [5.396113602391629, 2.7503736920777277]],
 [[6.606875934230194, 3.2137518684603883],
  [8.325859491778774, 3.2137518684603883],
  [7.473841554559042, 2.3617339312406576]]]
"""
polygon = Polygon(outer, holes)
viewpoint = (2,4.15) #(6.2, 2.4)
destination = [7, 7.5]
all_windows = [] # All of the windows we use
all_regions = {} # All of the regions we find by distance

# Compute  the initial visibility
vis_points = cast_rays_with_holes(polygon, viewpoint)
result_polys = Polygon(vis_points)

#Simplify the polygon to remove redundancy
result_polys = result_polys.simplify(tolerance=0.1, preserve_topology=True)
result_polys = [result_polys] # Convert to a list for easy computations

all_regions[0] = result_polys # add the initial region as the first entry

unvisited_polygon = polygon # Initiall, all unvisited
region_number = 0
region_groups = {}

while result_polys:
    # ***** Construct the next unvisited (not-visible) regions that remain *****
    # construct the clean unvisited polygon region(s)
    for poly in result_polys:
        unvisited_polygon = unvisited_polygon - poly.buffer(TOLERANCE)
        unvisited_polygon = unvisited_polygon.simplify(tolerance=0.1, preserve_topology=True)
    
    # If there is only one, make it into a multipolygon for ease
    if unvisited_polygon.geom_type == 'Polygon': 
        unvisited_polygon = MultiPolygon([unvisited_polygon])
    
    # ***** Marshal the unvisited polygons and windows together for processing *****
    work_groups = [[poly,[]] for poly in unvisited_polygon.geoms]
    
    #Find all the windows for the next step
    for group, poly in enumerate(unvisited_polygon.geoms):
        windows_segments = get_windows(polygon, poly)
        if windows_segments.geom_type == 'LineString':
            windows_segments = MultiLineString([windows_segments])
        current_windows = []
        for window in windows_segments.geoms:
            # Add the start point of the current LineString
            current_windows.append([window.coords[0], window.coords[-1]])
            for segment in current_windows: # Extract out the windows and group them in with the polygons
                    group, corrected = find_group(segment, unvisited_polygon)
                    work_groups[group][1].append(corrected) # Add the corrected segment to the correct group
    
    
    region_groups[region_number] = work_groups
    # ***** Project from the windows to the next set of visible regions *****
    result_polys = []
    for current_poly, current_windows in work_groups: # extract out the current polygon for processing
        new_vis_poly = Polygon()
        for vis_segment in current_windows:
            for vis_point in vis_segment:
                new_vis_points = cast_rays_with_holes(current_poly, vis_point)
                temp_poly = Polygon(new_vis_points)
                new_vis_poly = new_vis_poly.union(temp_poly)
    
        #Simplify the polygon to remove redundancy
        new_vis_poly = new_vis_poly.simplify(tolerance=0.1, preserve_topology=True)
        
        result_polys.append(new_vis_poly)
        all_windows += current_windows # add in all the working windows
    region_number += 1
    all_regions[region_number] = result_polys # add in the polygons for the current step


# ***** Solve the shortest- path problem *****














# ***** Final Cumulative Plot *****
colors = ['#AEDAE7', '#008A8A', '#3FE0D0', '#2D8B57', '#6E9AA7']

fig, ax = plt.subplots(figsize=(10, 10))
ox, oy = zip(*polygon.exterior.coords)
ax.plot(ox, oy, 'k-', label='Outer Boundary')

# Draw and label the original boundary
for interior in polygon.interiors:
    hx, hy = zip(*interior.coords)
    ax.plot(hx, hy, 'k-', label='Hole')
    ax.plot(hx, hy, 'b.', label='Vertices')    

    
# Draw the segmented interior of the polygon
for step, regions in all_regions.items():
    for i, region in enumerate(regions):
        vx, vy = zip(*region.exterior.coords)
        ax.plot(vx,vy, 'g.')
        if i == 0:
            ax.fill(vx, vy, color=colors[step%len(colors)], alpha=0.5, label='Visibility-' + str(step))
        else:
            ax.fill(vx, vy, color=colors[step%len(colors)], alpha=0.5)
            
# Draw all the windows
for i,item in enumerate(all_windows):
    px,py = zip(*item)
    if i == 0:
        ax.plot(px, py, "m-", label='Windows')
    else:
        ax.plot(px, py, "m-")

# Draw the starting point
ax.plot(*viewpoint, 'ro', label='Start')
ax.plot(destination[0], destination[1], 'go', label='Finish')

ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect('equal')
plt.title("Minimum-Link Visibility Polygon from a Starting Point")
plt.legend()
plt.show()

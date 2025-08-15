# -*- coding: utf-8 -*-
"""
Created on Fri Aug 15 15:54:24 2025

@author: histo
"""

def load_data_from_txt(file_path):
    boundary = []
    holes = []
    current_section = None

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue  # skip empty lines

            if line.startswith("OUTER"):
                current_section = "boundary"
                continue
            elif line.startswith("CLUSTER"):
                current_section = []
                holes.append(current_section)
                continue
            elif line.startswith("CENTERS"):
                break  # stop reading if we reach CENTERS section

            # parse coordinates
            if "," in line:
                x_str, y_str = line.split(",")
                point = (int(x_str.strip()), int(y_str.strip()))

                if current_section == "boundary":
                    boundary.append(point)
                elif isinstance(current_section, list):
                    current_section.append(point)

    return boundary, holes



file_path = "plotting images\exports\shape_vertices_2025-08-14_D.txt" 
boundary, holes = load_data_from_txt(file_path)

print("Boundary:", boundary)
print("\nHoles:")
for idx, hole in enumerate(holes):
    print(f"Hole {idx}:", hole)

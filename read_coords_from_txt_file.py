# -*- coding: utf-8 -*-
"""
Created on Fri Aug 15 15:54:24 2025

@author: histo
"""


def load_data_from_txt(file_path):
    boundary = []
    holes = []
    current_section = None

    with open(file_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue  # skip empty lines

            upper = line.upper()

            # Section headers
            if upper.startswith("OUTER"):
                current_section = "boundary"
                continue
            elif upper.startswith("CLUSTER") or upper.startswith("HOLE"):
                current_section = []
                holes.append(current_section)
                continue
            elif upper.startswith("CENTERS"):
                # optional section — stop reading geometry
                break

            # parse coordinates
            if "," in line:
                try:
                    x_str, y_str = line.split(",", 1)  # be tolerant of extra commas/spaces
                    point = (int(x_str.strip()), int(y_str.strip()))
                except ValueError:
                    # not a clean "x, y" line — ignore safely
                    continue

                if current_section == "boundary":
                    boundary.append(point)
                elif isinstance(current_section, list):
                    current_section.append(point)

    return boundary, holes


file_path = r"plotting images\vertices_output_with_holes.txt"
#file_path = r"plotting images\exports\shape_vertices_2025-08-14_D.txt"
boundary, holes = load_data_from_txt(file_path)

print("Boundary:", boundary)
print("\nHoles:")
for idx, hole in enumerate(holes):
    print(f"Hole {idx}:", hole)

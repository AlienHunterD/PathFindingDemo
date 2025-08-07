# -*- coding: utf-8 -*-
"""
Created on Fri Aug  1 17:18:33 2025

@author: histo
"""


import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def load_image(path):
    
    img = Image.open(path).convert("RGB")
    return np.array(img)

def extract_and_plot_vertices(image_path, epsilon_ratio=0.01):
    img = load_image(image_path)
    h, w = img.shape[:2]

    # Convert to grayscale and threshold
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        print("No contours found.")
        return []

    contour = max(contours, key=cv2.contourArea)

    # Approximate polygon from contour
    epsilon = epsilon_ratio * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    # Flip y axis for all points (so origin is bottom left)
    vertices = [(pt[0][0], h - pt[0][1]) for pt in approx]

    # Plot
    plt.figure(figsize=(6, 6))
   
    x, y = zip(*vertices)
    plt.plot(x + (x[0],), y + (y[0],), 'ro-')  # close polygon

    for i, (vx, vy) in enumerate(vertices):
        plt.text(vx + 5, vy, f'{i+1}', fontsize=9, color='blue')

    plt.title("Detected Vertices (0,0 = Bottom Left)")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.grid(True)
    plt.gca().set_aspect('equal')
    plt.xticks(np.arange(0, w+1, 50))
    plt.yticks(np.arange(0, h+1, 50))
    plt.show()

    return vertices

# Show Images
vertices = extract_and_plot_vertices("min_link_shape.png")  # < -- filename
print("Boundary Coordinates (x, y):")
for x, y in vertices:
    print(f"({int(x)}, {int(y)})")








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

def extract_vertices(image_path, epsilon_ratio=0.01):
    img = load_image(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Apply binary threshold
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if not contours:
        print("No contours found.")
        return

    # Get the largest contour (assume main shape)
    contour = max(contours, key=cv2.contourArea)

    # Approximate contour to polygon (reduce to vertices)
    epsilon = epsilon_ratio * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    # Extract vertices
    vertices = [(pt[0][0], pt[0][1]) for pt in approx]

    # Plot
    x, y = zip(*vertices)
    plt.figure(figsize=(6, 6))
    plt.imshow(np.ones_like(gray) * 255, cmap='gray')  # blank white
    plt.plot(contour[:,0,0], contour[:,0,1], '-', label='Contour')
    plt.plot(x + (x[0],), y + (y[0],), 'ro-')  # closed polygon
    for i, (vx, vy) in enumerate(vertices):
        plt.text(vx + 5, vy, f'{i+1}', fontsize=9, color='blue')
    
    plt.gca().set_aspect('equal')
    plt.title('Detected Vertices on Shape')
    plt.grid(True)
    plt.legend()
    plt.show()

    return vertices

# Example usage
vertices = extract_vertices("min_link_shape.png")  # Use any .jpg, .png, etc.
print("Vertices (x, y):", vertices)





from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import cv2

def get_dominant_and_central_background_color(image_path, k=3):
    image = Image.open(image_path)
    image = image.resize((224, 224))  # Resize for consistency

    # Convert image to NumPy array
    image_np = np.array(image)

    # Convert to grayscale and apply edge detection
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    # Invert edges to get a mask for the background (0 for edges, 255 for background)
    mask = cv2.bitwise_not(edges)
    
    # Mask the image to keep only the background pixels
    background_pixels = image_np[mask == 255]

    # Calculate the dominant background color
    if len(background_pixels) == 0:
        dominant_color = [0, 0, 0]  # Return black if no background pixels are detected
    else:
        # Apply k-means to the background pixels
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(background_pixels)

        # Get the most common color in the background (cluster center with most points)
        counts = np.bincount(kmeans.labels_)
        dominant_color = kmeans.cluster_centers_[np.argmax(counts)]
        dominant_color = [int(c) for c in dominant_color]  # Convert to integers

    # Calculate the central background color
    center_size = 50  # Define a region around the center (e.g., 50x50 pixels)
    center_x, center_y = image_np.shape[1] // 2, image_np.shape[0] // 2

    # Extract the central region
    central_region = image_np[center_y - center_size // 2:center_y + center_size // 2,
                              center_x - center_size // 2:center_x + center_size // 2]

    # Mask the central region to exclude edges
    central_region_masked = central_region[mask[center_y - center_size // 2:center_y + center_size // 2,
                                                 center_x - center_size // 2:center_x + center_size // 2] == 255]

    if len(central_region_masked) == 0:
        central_color = [0, 0, 0]  # Return black if no background pixels are detected in the center
    else:
        # Calculate the average color of the central region
        central_color = np.mean(central_region_masked, axis=0)
        central_color = [int(c) for c in central_color]  # Convert to integers

    return central_color


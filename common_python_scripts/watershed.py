import cv2
import numpy as np
from skimage import io, morphology, filters
from skimage.segmentation import watershed
from skimage.feature import peak_local_max
from shapely.geometry import Polygon
import tifffile as tiff
import geopandas as gpd
import argparse
import os
from shapely.affinity import translate
import pandas as pd
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from skimage.morphology import local_maxima
from skimage.filters import gaussian

def load_and_preprocess(image_path):
    image = io.imread(image_path)

    # Handle (1, H, W) → (H, W)
    if image.ndim == 3 and image.shape[0] == 1:
        image = image[0]

    # Convert to grayscale if RGB
    if image.ndim == 3:
        if image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        elif image.shape[2] == 1:
            gray = image.squeeze()
        else:
            raise ValueError(f"Unsupported channel count: {image.shape[2]}")
    else:
        gray = image  # Already (H, W)

    return gray

def generate_labels(gray):
    # Threshold with a 10% relaxed Yen value
    thresh = filters.threshold_yen(gray)
    binary = gray > (thresh * 0.9)

    # Distance transform
    distance = ndi.distance_transform_edt(binary)

    # Marker detection
    local_maxi = morphology.local_maxima(distance)
    local_maxi &= binary  # Restrict to valid regions
    markers, _ = ndi.label(local_maxi)

    # Smooth gradient before Sobel
    smoothed = gaussian(gray, sigma=1.0)
    gradient = filters.sobel(smoothed)

    # Watershed
    labels = watershed(gradient, markers=markers, mask=binary)
    return labels


def extract_polygons_from_labels(labels, min_area=5):  # lowered min_area
    mask = np.zeros_like(labels, dtype=np.uint8)
    polygons = []

    for label in np.setdiff1d(np.unique(labels), [0]):
        np.copyto(mask, (labels == label).astype(np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            if len(cnt) >= 3:
                cnt = cnt.reshape(-1, 2)
                poly = Polygon(cnt)
                if poly.area >= min_area:
                    # Auto-fix invalid polygons
                    if not poly.is_valid:
                        poly = poly.buffer(0)
                    if poly.is_valid:
                        polygons.append(poly)

    return polygons

def main(image_paths):
    image_paths = image_paths.split(",")

    for image_path in image_paths:
        gray = load_and_preprocess(image_path)
        labels = generate_labels(gray)
        polygons = extract_polygons_from_labels(labels)

        filename = os.path.basename(image_path)
        parts = filename.split(".")[0].split("_")
        suffix = f"{parts[2]}_{parts[3]}" if len(parts) >= 4 else "output"

        gdf = gpd.GeoDataFrame(geometry=polygons)
        gdf.to_parquet(f'cell_polygons_{suffix}.parquet')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Watershed cell segmentation')
    parser.add_argument('--image_paths', required=True, help='Path to the input TIFF image')
    args = parser.parse_args()

    main(args.image_paths)
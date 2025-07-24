import cv2
import numpy as np
from skimage import io, morphology
from scipy import ndimage as ndi
from skimage.segmentation import watershed
from skimage.filters import sobel
import tifffile as tiff
import geopandas as gpd
from shapely.geometry import Polygon
import argparse
import os

def load_and_preprocess(image_path):
    image = io.imread(image_path)

    if image.ndim == 3:
        if image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        elif image.shape[2] == 1:
            gray = image.squeeze()
        else:
            raise ValueError(f"Unsupported channel count: {image.shape[2]}")
    else:
        gray = image

    return gray

def generate_labels(gray):
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    distance = ndi.distance_transform_edt(binary)
    local_maxi = morphology.local_maxima(distance)
    markers, _ = ndi.label(local_maxi)
    gradient = sobel(gray)
    labels = watershed(gradient, markers, mask=binary)
    return labels

def extract_polygons_from_labels(labels):
    mask = np.zeros_like(labels, dtype=np.uint8)
    polygons = []

    for label in np.setdiff1d(np.unique(labels), [0]):
        np.copyto(mask, (labels == label).astype(np.uint8))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if len(cnt) >= 3:
                cnt = cnt.reshape(-1, 2)
                poly = Polygon(cnt)
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
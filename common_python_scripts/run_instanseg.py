import imagecodecs
import tifffile
from instanseg import InstanSeg
# from instanseg.inference_class import InstanSeg
import numpy as np
from aicsimageio import AICSImage
import torch
import os
import bioio
from instanseg.utils.utils import labels_to_features
import fastremap
from skimage import io
from pathlib import Path
from shapely.geometry import Polygon
import geopandas as gpd
import glob
import argparse
import ujson
import json

def main(image_paths_list, image_pixel_size, technology, subset_data_y_x_interval):

    def patched_save_output(self, image_path: str, labels: torch.Tensor, image_array=None, save_overlay=False, save_geojson=False):
        if isinstance(image_path, str):
            image_path = Path(image_path)
        if isinstance(labels, torch.Tensor):
            labels = labels.cpu().detach().numpy()

        new_stem = image_path.stem + self.prediction_tag

        if self.verbose:
            out_path = Path(image_path).parent / (new_stem + ".tiff")
            print(f"Saving output to {out_path}")
            io.imsave(out_path, labels.squeeze().astype(np.int32), check_contrast=False)

        if save_geojson:
            if labels.ndim == 3:
                labels = labels[None]

            output_dimension = labels.shape[1]
            if output_dimension == 1:
                features = labels_to_features(labels[0,0], object_type="detection")
            elif output_dimension == 2:
                features = (labels_to_features(labels[0,0], object_type="detection", classification="Nuclei") +
                            labels_to_features(labels[0,1], object_type="detection", classification="Cells"))

            geojson = json.dumps(features)
            geojson_path = Path(image_path).parent / (new_stem + ".geojson")

            print("Saving geojson...")
            with open(geojson_path, "w") as outfile:
                outfile.write(geojson)

        if save_overlay:
            assert image_array is not None, "Image array must be provided to save overlay."
            if self.verbose:
                out_path = Path(image_path).parent / (new_stem + "_overlay.tiff")
                print(f"Saving overlay to {out_path}")
            display = self.display(image_array, labels)
            io.imsave(out_path, display, check_contrast=False)

    InstanSeg.save_output = patched_save_output

    image_paths_list = image_paths_list.split(',')

    subset_data_y_x_interval = subset_data_y_x_interval.split(',')

    start_y, end_y, start_x, end_x = int(subset_data_y_x_interval[0]), int(subset_data_y_x_interval[1]), int(subset_data_y_x_interval[2]), int(subset_data_y_x_interval[3])

    if technology == "MERSCOPE":
        image_reader = 'tiffslide'

    elif technology == "Xenium":
        image_reader = 'bioio'

    instanseg_brightfield = InstanSeg("fluorescence_nuclei_and_cells", image_reader="tiffslide", verbosity=1)
    instanseg_brightfield.medium_image_threshold = end_x * end_y * 10

    labeled_output = instanseg_brightfield.eval(
        image=image_paths_list[0],
        save_output=True,
        save_overlay=True,
        save_geojson=True,
        pixel_size=image_pixel_size,
        target = "cells"
    )

    # directory_path = os.getcwd()
    # geojson_files = []

    # for root, dirs, files in os.walk(directory_path):
    #     for file in files:
    #         if file.endswith('.geojson'):
    #             geojson_files.append(os.path.join(root, file))

    # with open(geojson_files[0]) as file:
    #     data = json.load(file)

    # polygons = []

    # for entry in data:
    #     coordinates_list = entry['geometry']['coordinates'][0]
    #     polygons.append(Polygon(coordinates_list))

    # polygons_geo_df = gpd.GeoDataFrame(geometry=polygons)

    # Efficient file finding
    directory_path = os.getcwd()
    geojson_path = next(
        os.path.join(directory_path, f)
        for f in os.listdir(directory_path)
        if f.endswith(".geojson")
    )

    # Fast JSON loading
    with open(geojson_path, "r") as f:
        data = ujson.load(f)

    # Vectorized geometry construction
    polygons = [Polygon(np.array(e['geometry']['coordinates'][0])) for e in data]

    # Construct GeoDataFrame
    polygons_geo_df = gpd.GeoDataFrame(geometry=polygons)

    polygons_geo_df.to_parquet("cell_polygons.parquet")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='instanseg_implementation')
    parser.add_argument('--image_paths_list')
    parser.add_argument('--image_pixel_size', type=float)
    parser.add_argument('--technology')
    parser.add_argument('--subset_data_y_x_interval')
    args = parser.parse_args()

    main(image_paths_list = args.image_paths_list,
         image_pixel_size = args.image_pixel_size,
         technology = args.technology,
         subset_data_y_x_interval = args.subset_data_y_x_interval)
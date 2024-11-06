import imagecodecs
import tifffile
from instanseg import InstanSeg
import numpy as np
from aicsimageio import AICSImage
import torch
import os
import bioio
from instanseg.utils.utils import labels_to_features
import fastremap
from skimage import io
from pathlib import Path
import json
from shapely.geometry import Polygon
import geopandas as gpd
import glob
import argparse

def main(image_paths_list, image_pixel_size):

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
            with open(os.path.join(geojson_path), "w") as outfile:
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
    
    image = tifffile.imread(image_paths_list[0])

    instanseg_brightfield = InstanSeg("fluorescence_nuclei_and_cells", image_reader="bioio", verbosity=1)
    instanseg_brightfield.medium_image_threshold = image.shape[1] * image.shape[2] * 10

    labeled_output = instanseg_brightfield.eval(
        image=image_paths_list[0],
        save_output=True,
        save_overlay=True,
        save_geojson=True,
        pixel_size=image_pixel_size,
        normalisation_subsampling_factor=10,
        target = "cells"
    )

    geojson_files = glob.glob("*.geojson")

    if geojson_files:
        geojson_file_path = geojson_files[0]
    else:
        print("No GeoJSON file found.")

    with open(geojson_file_path) as file:
        data = json.load(file)

    polygons = []

    for entry in data:
        coordinates_list = entry['geometry']['coordinates'][0]
        polygons.append(Polygon(coordinates_list))

    polygons_geo_df = gpd.GeoDataFrame(geometry=polygons)

    polygons_geo_df.to_parquet("cell_polygons.parquet")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='instanseg')
    parser.add_argument('--image_paths_list')
    parser.add_argument('--image_pixel_size', type=float)
    args = parser.parse_args()

    main(image_paths_list = args.image_paths_list,
         image_pixel_size = args.image_pixel_size)
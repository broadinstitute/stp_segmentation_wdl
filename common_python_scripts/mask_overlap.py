import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
from skimage.io import imread
from skimage import measure
from shapely import geometry
import time
import geopandas
from shapely.wkb import dumps
from shapely.geometry import Polygon
import rtree

def convert_to_px(conversion, mat):
    """This function transforms coordinates from um to px given a conversion matrix 
    
    Parameters
    -----------
    conversion: conversion matrix from vizgen the file is called micron_to_mosaic_pixel_transform
    mat: pandas df of x and y coordinates
    Returns
    -----------
    xcoord_transformed: X coordinate with new origin and scaled
    ycoord_transformed: Y coordinate with new origin and scaled
    """
        
    mat = np.array(mat)
    new_col = np.ones((mat.shape[0], 1))
    all_data = np.concatenate((mat, new_col), 1)
    
    # affine transform
    transformed_mat = (conversion @ np.array(all_data.T)).T
    
    return [transformed_mat[[0]], transformed_mat[[1]]]

def parse_outline_to_polygon(outline_str):
        numbers = list(map(int, outline_str.split(',')))
        points = [(numbers[i], numbers[i + 1]) for i in range(0, len(numbers), 2)]
        return Polygon(points)

def main(detected_transcripts, transform, outlines, out_path):

    df_detected_transcripts = pd.read_csv(detected_transcripts)
    df_detected_transcripts =  df_detected_transcripts.drop("Unnamed: 0", axis = 1)
    
    df_transform = pd.read_csv(transform, 
                        header = None,
                        sep = " ")
    
    x_px, y_px = convert_to_px(df_transform, df_detected_transcripts[["global_x", "global_y"]])
    df_detected_transcripts["x_px"] = x_px
    df_detected_transcripts["y_px"] = y_px
    
    df_detected_transcripts["Index"] = df_detected_transcripts.index + 1
    
    # Read the file and parse each line into a Polygon
    polygons = []
    with open(outlines, 'r') as file:
        for line in file:
            line = line.strip()  # Remove newline character and any leading/trailing whitespace
            if line:  # Check if line is not empty
                polygon = parse_outline_to_polygon(line)
                polygons.append(polygon)

    df_polygons = pd.DataFrame({":cell": range(0, len(polygons))})
        
    df_polygons_geo = geopandas.GeoDataFrame(
        df_polygons, geometry=polygons)
        
    df_detected_transcripts_geo = geopandas.GeoDataFrame(
        df_detected_transcripts, geometry=geopandas.points_from_xy(df_detected_transcripts['x_px'], 
                                                     df_detected_transcripts['y_px']))

    index = df_detected_transcripts_geo.sindex
    index.properties = rtree.index.Property(leaf_capacity = 3000, 
                                        fill_factor = 0.9)

    df_geo_join = geopandas.sjoin(df_polygons_geo, df_detected_transcripts_geo, how='left')
    df_geo_join = df_geo_join[df_geo_join['Index'].notna()]
    df_geo_join = df_geo_join[[":cell", "geometry", "Index"]]
    out_df = df_detected_transcripts_geo.merge(df_geo_join, how = 'left', on = "Index")

    out_df =out_df.drop_duplicates(subset="Index")
    out_df[":cell"] = out_df[":cell"].fillna(0)
    out_df[":cell"] = out_df[":cell"].astype(int)
        
    out_df['geometry_x'] = out_df['geometry_x'].apply(lambda geom: dumps(geom, hex=True))
    out_df['geometry_y'] = out_df['geometry_y'].apply(lambda geom: dumps(geom, hex=True))

    out_df.to_csv(out_path + "detected_transcripts_cellID_geo.csv")
    
    out_df.to_parquet(out_path + 'detected_transcripts_cellID_geo.parquet')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='segmentation to transcripts')
    parser.add_argument('--outlines')
    parser.add_argument('--out_path')
    parser.add_argument('--transform')
    parser.add_argument('--detected_transcripts')
    args = parser.parse_args()

    main(outlines = args.outlines,
        out_path = args.out_path,
        transform = args.transform,
        detected_transcripts = args.detected_transcripts)

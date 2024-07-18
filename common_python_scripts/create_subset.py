import numpy as np
import tifffile as tiff
import argparse
import pandas as pd
from skimage.exposure import equalize_adapthist
from tiling_script import tiling_script
import tile_intervals
import os

def main(image_paths_list, subset_data_y_x_interval, transform_file, detected_transcripts_file, technology, tiles_dimension, overlap, amount_of_VMs):

    channel_images = []

    image_paths_list = image_paths_list.split(',')

    subset_data_y_x_interval = subset_data_y_x_interval.split(',')

    start_y, end_y, start_x, end_x = int(subset_data_y_x_interval[0]), int(subset_data_y_x_interval[1]), int(subset_data_y_x_interval[2]), int(subset_data_y_x_interval[3])

    for image_path in image_paths_list:

        with tiff.TiffFile(image_path, is_ome=False) as image_file:

            series = image_file.series[0]
            plane = series.pages[0]

            subset_channel_image = equalize_adapthist(plane.asarray()[start_x:end_x, start_y:end_y], kernel_size=[100, 100], clip_limit=0.01, nbins=256)

            channel_images.append(subset_channel_image)

    subset_multi_channel_image = np.stack(channel_images, axis=0)

    listed_intervals = tile_intervals.tile_intervals(subset_multi_channel_image, tiles_dimension, overlap, amount_of_VMs)
    num_VMs_in_use = listed_intervals['number_of_VMs'][0][0]
    out_path=os.getcwd()

    for shard_index in range(num_VMs_in_use):

        tiling_script(subset_multi_channel_image, listed_intervals, shard_index, out_path)

    #tiff.imwrite('subset_multi_channel_image.tiff', subset_multi_channel_image, photometric='minisblack', metadata={'axes': 'CYX'})

    if technology == 'MERSCOPE':
        transform_df = pd.read_csv(transform_file, header=None, delimiter=" ")
        transformation_matrix = np.array([transform_df[0], transform_df[1], transform_df[2]])    

        detected_transcripts_df = pd.read_csv(detected_transcripts_file)
        x_col = 'global_x'
        y_col = 'global_y'       

    elif technology == 'XENIUM':
        transformation_matrix = pd.read_csv(transform_file).values[:3,:3]

        detected_transcripts_df = pd.read_parquet(detected_transcripts_file)
        x_col = 'x_location'
        y_col = 'y_location'  

    inverse_transformation_matrix = np.linalg.inv(transformation_matrix)

    pixel_bounds = np.array([[start_x, start_y, 1],
                                [end_x, end_y, 1]])

    # Convert pixel bounds to micron coordinates
    micron_coordinates = np.dot(inverse_transformation_matrix, pixel_bounds.T).T

    # Removing the homogeneous coordinate, if not necessary
    micron_coordinates = micron_coordinates[:, :2]

    x_min = micron_coordinates[0,0]
    x_max = micron_coordinates[1,0]

    y_min = micron_coordinates[0,1]
    y_max = micron_coordinates[1,1]

    trx_subset = detected_transcripts_df[(detected_transcripts_df[x_col] >= x_min) & 
                (detected_transcripts_df[x_col] < x_max) & 
                (detected_transcripts_df[y_col] >= y_min) & 
                (detected_transcripts_df[y_col] < y_max) 
                ]

    temp = trx_subset[[x_col, y_col]].values
    transcript_positions = np.ones((temp.shape[0], temp.shape[1]+1))
    transcript_positions[:, :-1] = temp

    # Transform coordinates to mosaic pixel coordinates

    transformed_positions = np.matmul(transformation_matrix, np.transpose(transcript_positions))[:-1]
    trx_subset.loc[:, 'local_x'] = transformed_positions[0, :]
    trx_subset.loc[:,'local_y'] = transformed_positions[1, :]

    trx_subset['local_x'] = trx_subset['local_x'] - start_x
    trx_subset['local_y'] = trx_subset['local_y'] - start_y

    trx_subset = trx_subset.drop([x_col, y_col], axis=1)
    trx_subset = trx_subset.rename(columns={'local_x': x_col, 'local_y': y_col})

    trx_subset.to_csv("subset_coordinates.csv")

    transformation_matrix_subset = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ])

    np.savetxt('subset_transformation_matrix.csv', transformation_matrix_subset, delimiter=' ', fmt='%d')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='composite_image_creation')
    parser.add_argument('--image_paths_list')
    parser.add_argument('--subset_data_y_x_interval')
    parser.add_argument('--transform_file')
    parser.add_argument('--detected_transcripts_file')
    parser.add_argument('--technology')
    parser.add_argument('--tiles_dimension', type=float)
    parser.add_argument('--overlap', type=float)
    parser.add_argument('--amount_of_VMs', type=float)
    args = parser.parse_args()

    main(image_paths_list = args.image_paths_list,  
        subset_data_y_x_interval = args.subset_data_y_x_interval,
        transform_file = args.transform_file,
        detected_transcripts_file = args.detected_transcripts_file,
        technology = args.technology,
        tiles_dimension = args.tiles_dimension, 
        overlap = args.overlap, 
        amount_of_VMs = args.amount_of_VMs)
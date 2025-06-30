import numpy as np
import tifffile as tiff
import argparse
import pandas as pd
from skimage.exposure import equalize_adapthist
from tiling_script import tiling_script
import tile_intervals
import os
import pyarrow.parquet as pq
import imagecodecs
from scipy.ndimage import gaussian_filter
import geopandas as gpd

def main(image_paths_list, subset_data_y_x_interval, transform_file, detected_transcripts_file, technology, tiles_dimension, overlap, amount_of_VMs, transcript_plot_as_channel, sigma, algorithm, trim_amount=50):

    channel_images = []
    mean_intensity_of_channels = {}

    image_paths_list = image_paths_list.split(',')

    subset_data_y_x_interval = subset_data_y_x_interval.split(',')

    start_y, end_y, start_x, end_x = int(subset_data_y_x_interval[0]), int(subset_data_y_x_interval[1]), int(subset_data_y_x_interval[2]), int(subset_data_y_x_interval[3])

    if technology == 'MERSCOPE':

        df_trx = pd.read_parquet(detected_transcripts_file, columns=["global_x", "global_y",'transcript_id', 'gene', 'fov'])

        transformation_matrix = pd.read_csv(transform_file, header=None, delimiter=" ").values[:3,:3]

        coords = np.column_stack((df_trx["global_x"].values, df_trx["global_y"].values))

        coeffs = [
            transformation_matrix[0, 0],  # a
            transformation_matrix[0, 1],  # b
            transformation_matrix[1, 0],  # d
            transformation_matrix[1, 1],  # e
            transformation_matrix[0, 2],  # xoff
            transformation_matrix[1, 2]   # yoff
        ]

        # Step 2: Build affine matrix and apply
        a, b, d, e, xoff, yoff = coeffs
        affine_matrix = np.array([[a, b], [d, e]])
        offset = np.array([xoff, yoff])

        # Apply transformation
        transformed_coords = coords @ affine_matrix.T + offset

        # transformed_coords is Nx2 numpy array
        x_coords = transformed_coords[:, 0]
        y_coords = transformed_coords[:, 1]

        # Create GeoSeries of points very efficiently
        geometry = gpd.points_from_xy(x_coords, y_coords)

        df_trx["geometry_micron"] = gpd.points_from_xy(df_trx["global_x"], df_trx["global_y"])

        df_trx.drop(['global_x','global_y'], axis=1, inplace=True)

        gdf_transcripts = gpd.GeoDataFrame(df_trx, geometry=geometry)

        gdf_transcripts.rename(columns={'geometry':'geometry_image_space', 'geometry_micron': 'geometry'}, inplace=True)
        gdf_transcripts.set_geometry('geometry_image_space', inplace=True)

        gdf_transcripts.to_parquet("subset_coordinates.parquet")

        # transform_df = pd.read_csv(transform_file, header=None, delimiter=" ")
        # df = pd.read_parquet("subset_coordinates.parquet", columns=["global_x", "global_y",'transcript_id', 'gene'])

        # coords = np.column_stack((df["global_x"].values, df["global_y"].values))

        # coeffs = [
        #     transformation_matrix[0, 0],  # a
        #     transformation_matrix[0, 1],  # b
        #     transformation_matrix[1, 0],  # d
        #     transformation_matrix[1, 1],  # e
        #     transformation_matrix[0, 2],  # xoff
        #     transformation_matrix[1, 2]   # yoff
        # ]

        # # Step 2: Build affine matrix and apply
        # a, b, d, e, xoff, yoff = coeffs
        # affine_matrix = np.array([[a, b], [d, e]])
        # offset = np.array([xoff, yoff])

        # # Apply transformation
        # transformed_coords = coords @ affine_matrix.T + offset

        # # transformed_coords is Nx2 numpy array
        # x_coords = transformed_coords[:, 0]
        # y_coords = transformed_coords[:, 1]

        # # Create GeoSeries of points very efficiently
        # geometry = gpd.points_from_xy(x_coords, y_coords)

        # gdf_transcripts = gpd.GeoDataFrame(df, geometry=geometry)

        # transformation_matrix = np.array([
        #                             [transform_df[0][0], transform_df[1][0], transform_df[2][0]],
        #                             [transform_df[0][1], transform_df[1][1], transform_df[2][1]],
        #                             [transform_df[0][2], transform_df[1][2], transform_df[2][2]]
        #                         ])

        # inverse_transformation_matrix = np.linalg.inv(transformation_matrix)

        # pixel_bounds = np.array([[start_x, start_y, 1],
        #                             [end_x, end_y, 1]])

        # # Convert pixel bounds to micron coordinates
        # micron_coordinates = np.dot(inverse_transformation_matrix, pixel_bounds.T).T

        # # Removing the homogeneous coordinate, if not necessary
        # micron_coordinates = micron_coordinates[:, :2]

        # x_min = micron_coordinates[0,0]
        # x_max = micron_coordinates[1,0]

        # y_min = micron_coordinates[0,1]
        # y_max = micron_coordinates[1,1]

        # x_col = 'global_x'
        # y_col = 'global_y'

        # # chunk_size = 100000
        # # trx_subset = pd.DataFrame()

        # # for chunk in pd.read_csv(detected_transcripts_file, chunksize=chunk_size):

        # #     trx_subset_temp = chunk[(chunk[x_col] >= x_min) &
        # #                 (chunk[x_col] < x_max) &
        # #                 (chunk[y_col] >= y_min) &
        # #                 (chunk[y_col] < y_max)
        # #                 ]

        # #     trx_subset = pd.concat([trx_subset, trx_subset_temp])

        # batch_size = 100000
        # batch_list = []
        # trx_subset = pd.DataFrame()

        # parquet_file = pq.ParquetFile(detected_transcripts_file)

        # for batch in parquet_file.iter_batches(batch_size=batch_size):

        #     batch_df = batch.to_pandas()

        #     trx_subset_temp = batch_df[
        #         (batch_df[x_col] >= x_min) &
        #         (batch_df[x_col] < x_max) &
        #         (batch_df[y_col] >= y_min) &
        #         (batch_df[y_col] < y_max)
        #     ]
        #     batch_list.append(trx_subset_temp)

        # trx_subset = pd.concat(batch_list, ignore_index=True)

    elif technology == 'Xenium':
        transformation_matrix = pd.read_csv(transform_file, sep=' ', header=None).values[:3,:3]

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

        x_col = 'x_location'
        y_col = 'y_location'

        batch_size = 100000
        batch_list = []
        trx_subset = pd.DataFrame()

        parquet_file = pq.ParquetFile(detected_transcripts_file)

        for batch in parquet_file.iter_batches(batch_size=batch_size):

            batch_df = batch.to_pandas()

            trx_subset_temp = batch_df[
                (batch_df[x_col] >= x_min) &
                (batch_df[x_col] < x_max) &
                (batch_df[y_col] >= y_min) &
                (batch_df[y_col] < y_max)
            ]
            batch_list.append(trx_subset_temp)

        trx_subset = pd.concat(batch_list, ignore_index=True)

    # temp = trx_subset[[x_col, y_col]].values
    # transcript_positions = np.ones((temp.shape[0], temp.shape[1]+1))
    # transcript_positions[:, :-1] = temp

    # # Transform coordinates to mosaic pixel coordinates

    # transformed_positions = np.matmul(transformation_matrix, np.transpose(transcript_positions))[:-1]
    # trx_subset.loc[:, 'local_x'] = transformed_positions[0, :]
    # trx_subset.loc[:,'local_y'] = transformed_positions[1, :]

    # trx_subset['local_x'] = trx_subset['local_x'] - start_x
    # trx_subset['local_y'] = trx_subset['local_y'] - start_y

    # trx_subset = trx_subset.drop([x_col, y_col], axis=1)
    # trx_subset = trx_subset.rename(columns={'local_x': x_col, 'local_y': y_col})

    # trx_subset.to_csv("subset_coordinates.csv")

    transformation_matrix_subset = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ])

    np.savetxt('subset_transformation_matrix.csv', transformation_matrix_subset, delimiter=' ', fmt='%d')

    for image_index, image_path in enumerate(image_paths_list):

        with tiff.TiffFile(image_path, is_ome=False) as image_file:

            series = image_file.series[0]
            plane = series.pages[0]

            subset_channel_image = equalize_adapthist(plane.asarray()[start_y:end_y, start_x:end_x], kernel_size=[100, 100], clip_limit=0.01, nbins=256)

            # mean_intensity_of_channels[f"{image_index}_indexed_image"] = np.mean(subset_channel_image)

            channel_images.append(subset_channel_image)

    # mean_intensity_of_channels_df = pd.DataFrame(mean_intensity_of_channels, index=[0])
    # mean_intensity_of_channels_df.to_csv('mean_intensity_of_channels.csv', index=False)

    # if transcript_plot_as_channel == 1:
    #     array_x = trx_subset[x_col].values
    #     array_y = trx_subset[y_col].values

    #     image_size = (end_y-start_y, end_x-start_x)

    #     transcript_image = np.zeros(image_size, dtype=np.uint8)

    #     x_coords = np.clip(array_x.astype(int), 0, image_size[1] - 1)
    #     y_coords = np.clip(array_y.astype(int), 0, image_size[0] - 1)

    #     intensity = 255
    #     point_size = 3

    #     for x, y in zip(x_coords, y_coords):
    #         transcript_image[max(0, y-point_size//2):min(image_size[0], y+point_size//2+1),
    #             max(0, x-point_size//2):min(image_size[1], x+point_size//2+1)] = intensity

    #     blurred_transcript_image = gaussian_filter(transcript_image, sigma=sigma)
    #     channel_images.append(blurred_transcript_image)

    subset_multi_channel_image = np.stack(channel_images, axis=0)

    out_path=os.getcwd()

    if algorithm != 'Instanseg':

        listed_intervals = tile_intervals.tile_intervals(subset_multi_channel_image, tiles_dimension, overlap, amount_of_VMs, trim_amount)
        num_VMs_in_use = listed_intervals['number_of_VMs'][0][0]

        for shard_index in range(num_VMs_in_use):

            tiling_script(subset_multi_channel_image, listed_intervals, shard_index, out_path)

    else:
        tiling_script(subset_multi_channel_image, out_path, algorithm)

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
    parser.add_argument('--transcript_plot_as_channel', type=int)
    parser.add_argument('--sigma', type=int)
    parser.add_argument('--algorithm', type=str)
    parser.add_argument('--trim_amount', type=int)
    args = parser.parse_args()

    main(image_paths_list = args.image_paths_list,
        subset_data_y_x_interval = args.subset_data_y_x_interval,
        transform_file = args.transform_file,
        detected_transcripts_file = args.detected_transcripts_file,
        technology = args.technology,
        tiles_dimension = args.tiles_dimension,
        overlap = args.overlap,
        amount_of_VMs = args.amount_of_VMs,
        transcript_plot_as_channel = args.transcript_plot_as_channel,
        sigma = args.sigma,
        algorithm = args.algorithm,
        trim_amount = args.trim_amount)
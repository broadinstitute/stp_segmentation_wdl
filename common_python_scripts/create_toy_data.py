import numpy as np
import tifffile as tiff
import argparse
import pandas as pd

def main(image_paths_list, toy_data_x_interval, toy_data_y_interval, transform_file, detected_transcripts_file):

    channel_images = []

    image_paths_list = image_paths_list.split(',')

    for image_path in image_paths_list:
        channel_image = tiff.imread(image_path)
        channel_images.append(channel_image)
    
    multi_channel_image = np.stack(channel_images, axis=0)

    start_y, end_y = int(toy_data_y_interval[0]), int(toy_data_y_interval[1])
    start_x, end_x = int(toy_data_x_interval[0]), int(toy_data_x_interval[1])

    toy_multi_channel_image = multi_channel_image[:, start_y:end_y, start_x:end_x]

    tiff.imwrite('toy_multi_channel_image.tiff', toy_multi_channel_image, photometric='minisblack', metadata={'axes': 'CYX'})

    transform_df = pd.read_csv(transform_file, header=None, delimiter=" ")
    transformation_matrix = np.array([transform_df[0], transform_df[1], transform_df[2]])

    # Calculate the inverse of the transformation matrix
    inverse_transformation_matrix = np.linalg.inv(transformation_matrix)

    # Example pixel bounds (x_min, y_min, x_max, y_max)
    pixel_bounds = np.array([[start_x, start_y, 1],  # Adding a ones column for affine transformation
                            [end_x, end_y, 1]])

    # Convert pixel bounds to micron coordinates
    micron_coordinates = np.dot(inverse_transformation_matrix, pixel_bounds.T).T

    # Removing the homogeneous coordinate, if not necessary
    micron_coordinates = micron_coordinates[:, :2]

    detected_transcripts_df = pd.read_csv(detected_transcripts_file)

    x_min = micron_coordinates[0,0]
    x_max = micron_coordinates[1,0]

    y_min = micron_coordinates[0,1]
    y_max = micron_coordinates[1,1]

    trx_subset = detected_transcripts_df[(detected_transcripts_df['global_x'] >= x_min) & 
                (detected_transcripts_df['global_x'] < x_max) & 
                (detected_transcripts_df['global_y'] >= y_min) & 
                (detected_transcripts_df['global_y'] < y_max) 
                ]

    temp = trx_subset[['global_x', 'global_y']].values
    transcript_positions = np.ones((temp.shape[0], temp.shape[1]+1))
    transcript_positions[:, :-1] = temp

    # Transform coordinates to mosaic pixel coordinates

    transformed_positions = np.matmul(transformation_matrix, np.transpose(transcript_positions))[:-1]
    trx_subset.loc[:, 'local_x'] = transformed_positions[0, :]
    trx_subset.loc[:,'local_y'] = transformed_positions[1, :]

    trx_subset['local_x'] = trx_subset['local_x'] - start_x
    trx_subset['local_y'] = trx_subset['local_y'] - start_y

    trx_subset = trx_subset.drop(['Unnamed: 0', 'global_x', 'global_y'], axis=1)
    trx_subset = trx_subset.rename(columns={'local_x': 'global_x', 'local_y': 'global_y'})

    trx_subset.to_csv("toy_coordinates.csv")

    transformation_matrix_toy = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ])

    np.savetxt('toy_transformation_matrix.csv', transformation_matrix_toy, delimiter=' ', fmt='%d')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='composite_image_creation')
    parser.add_argument('--image_paths_list')
    parser.add_argument('--toy_data_x_interval')
    parser.add_argument('--toy_data_y_interval')
    parser.add_argument('--transform_file')
    parser.add_argument('--detected_transcripts_file')
    args = parser.parse_args()

    main(image_paths_list = args.image_paths_list,  
        toy_data_x_interval = args.toy_data_x_interval,
        toy_data_y_interval = args.toy_data_y_interval,
        transform_file = args.transform_file,
        detected_transcripts_file = args.detected_transcripts_file)
version 1.0
task create_subset {

	input {       
    	Array[File] image_paths_list
        Array[Int] subset_data_y_x_interval
        File transform_file
        File detected_transcripts_file
        String technology
        Float tiles_dimension
        Float overlap
        Float amount_of_VMs 
        Int transcript_plot_as_channel
        Int sigma
        Int trim_amount
    }

    command <<<

        python /opt/create_subset.py --image_paths_list ~{sep=',' image_paths_list} \
                                       --subset_data_y_x_interval ~{sep=',' subset_data_y_x_interval} \
                                       --transform_file ~{transform_file} \
                                       --detected_transcripts_file ~{detected_transcripts_file} \
                                       --technology ~{technology} \
                                       --tiles_dimension ~{tiles_dimension} \
                                       --overlap ~{overlap} \
                                       --amount_of_VMs ~{amount_of_VMs} \
                                       --transcript_plot_as_channel ~{transcript_plot_as_channel} \
                                       --sigma ~{sigma} \
                                       --trim_amount ~{trim_amount}

    >>>

    output {
        File subset_coordinates = "subset_coordinates.csv"
        File subset_transformation_matrix = "subset_transformation_matrix.csv"
        File intervals = "intervals.json"
        Array[File] tile_metadata = glob("tile_metadata_*.csv")
        Array[File] tiled_image = glob("tiled_image_*.tiff")
        File original_tile_polygons = "original_tile_polygons.parquet"
        File trimmed_tile_polygons = "trimmed_tile_polygons.parquet"
        File mean_intensity_of_channels = "mean_intensity_of_channels.csv"
    }

    runtime {
        docker: "jishar7/subset_data_for_terra@sha256:08765521bcfe3be2ec18427942d050cef7b8e9d9ce9223afb4de9ab971421318"
        memory: "100GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
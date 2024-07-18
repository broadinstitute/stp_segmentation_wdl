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
    }

    command <<<

        python /opt/create_subset.py --image_paths_list ~{sep=',' image_paths_list} \
                                       --subset_data_y_x_interval ~{sep=',' subset_data_y_x_interval} \
                                       --transform_file ~{transform_file} \
                                       --detected_transcripts_file ~{detected_transcripts_file} \
                                       --technology ~{technology} \
                                       --tiles_dimension ~{tiles_dimension} \
                                       --overlap ~{overlap} \
                                       --amount_of_VMs ~{amount_of_VMs}

    >>>

    output {
        File subset_coordinates = "subset_coordinates.csv"
        File subset_transformation_matrix = "subset_transformation_matrix.csv"
        File intervals = "intervals.json"
        Array[File] tile_metadata = glob("tile_metadata_*.csv")
        Array[File] tiled_image = glob("tiled_image_*.tiff")
    }

    runtime {
        docker: "jishar7/subset_data_for_mac@sha256:c0118eb055f165e2d0eabc75d21a8114bc996d4403cc3ddbe6769edba9a079e4"
        memory: "100GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
version 1.0
task create_subset {

	input {       
    	Array[File] image_paths_list
        Array[Int] subset_data_x_interval
        Array[Int] subset_data_y_interval
        File transform_file
        File detected_transcripts_file
        String technology
    }

    command <<<

        python /opt/create_subset.py --image_paths_list ~{sep=',' image_paths_list} \
                                       --subset_data_x_interval ~{sep=',' subset_data_x_interval} \
                                       --subset_data_y_interval ~{sep=',' subset_data_y_interval} \
                                       --transform_file ~{transform_file} \
                                       --detected_transcripts_file ~{detected_transcripts_file} \
                                       --technology ~{technology}

    >>>

    output {
        File subset_multi_channel_image = "subset_multi_channel_image.tiff"
        File subset_coordinates = "subset_coordinates.csv"
        File subset_transformation_matrix = "subset_transformation_matrix.csv"
    }

    runtime {
        docker: "jishar7/subset_data_for_mac@sha256:099ad22e41031808b7cf790c0987895f0ea8aa4b46aae59c5a3b8e1e3e9db85a"
        memory: "50GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
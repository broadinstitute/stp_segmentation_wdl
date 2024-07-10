version 1.0
task create_toy_data {

	input {       
    	Array[File] image_paths_list
        Array[Int] toy_data_x_interval
        Array[Int] toy_data_y_interval
        File transform_file
        File detected_transcripts_file
    }

    command <<<

        python /opt/create_toy_data.py --image_paths_list ~{sep=',' image_paths_list} \
                                       --toy_data_x_interval ~{sep=',' toy_data_x_interval} \
                                       --toy_data_y_interval ~{sep=',' toy_data_y_interval} \
                                       --transform_file ~{transform_file} \
                                       --detected_transcripts_file ~{detected_transcripts_file}

    >>>

    output {
        File toy_multi_channel_image = "toy_multi_channel_image.tiff"
        File toy_coordinates = "toy_coordinates.csv"
        File toy_transformation_matrix = "toy_transformation_matrix.csv"
    }

    runtime {
        docker: "jishar7/toy_dataset_for_terra@sha256:b63fbffdcd576ad6969611bf6c953da2fe912ea912d29cd9fc8d73846c46e062"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
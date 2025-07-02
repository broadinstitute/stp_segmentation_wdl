version 1.0
task instanseg {

    input {
        Array[File]? image_paths_list
        Float? image_pixel_size
        String? technology
        Array[Int]? subset_data_y_x_interval
    }

    command <<<

        python /opt/run_instanseg.py --image_paths_list ~{sep=',' image_paths_list} \
                                --image_pixel_size ~{image_pixel_size} \
                                --technology ~{technology} \
                                --subset_data_y_x_interval ~{sep=',' subset_data_y_x_interval}

    >>>

    output {
        File processed_cell_polygons = "cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/instanseg@sha256:2e3930f51de503ff9386a2bf5a9fb85c8712516b4e69331b05e9b0a89c3b0f41"
        memory: "580GB"
        preemptible: 0
        cpu: 32
        disks: "local-disk 200 HDD"
    }

}
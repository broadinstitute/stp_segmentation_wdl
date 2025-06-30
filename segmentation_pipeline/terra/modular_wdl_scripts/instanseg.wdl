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
                                --subset_data_y_x_interval ~{subset_data_y_x_interval}

    >>>

    output {
        File processed_cell_polygons = "cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/instanseg@sha256:a858519679f7df174d9d066a0f49581c572225a5cb5a89ad50da5f312df8519b"
        memory: "400GB"
        preemptible: 0
        cpu: 32
        disks: "local-disk 200 HDD"
    }

}
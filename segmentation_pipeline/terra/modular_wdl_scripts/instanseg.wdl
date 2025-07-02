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
        docker: "jishar7/instanseg@sha256:2b700b8ceb3d6c69799afb2581aa8ed915055be707214ac0a402125c8f7c05b2"
        memory: "580GB"
        preemptible: 0
        cpu: 32
        disks: "local-disk 200 HDD"
    }

}
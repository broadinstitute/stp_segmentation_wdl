version 1.0
task instanseg {

    input {
        Array[File]? image_paths_list
        Float? image_pixel_size
    }

    command <<<

        python /opt/run_instanseg.py --image_paths_list ~{sep=',' image_paths_list} \
                                --image_pixel_size ~{image_pixel_size}

    >>>

    output {
        File processed_cell_polygons = "cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/instanseg@sha256:52c3b8b057e34ffc36d2cf76d83f23e0158d655b8ddb061ddebe21c0f708a21b"
        memory: "400GB"
        preemptible: 0
        cpu: 32
        disks: "local-disk 200 HDD"
    }

}
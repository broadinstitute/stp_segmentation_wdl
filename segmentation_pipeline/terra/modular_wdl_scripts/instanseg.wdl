version 1.0
task instanseg {

    input {
        Array[File] image_paths_list
        Float image_pixel_size
    }

    command <<<

        python /opt/instanseg.py --image_paths_list ~{sep=',' image_paths_list} \
                                --image_pixel_size ~{image_pixel_size}

    >>>

    output {
        File processed_cell_polygons = "cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/instanseg@sha256:ac93dd9e509cbb371eef9dfa0378fec6cf37f80512309f57338be98c368e85f8"
        memory: "120GB"
        preemptible: 2
        cpu: 32
        disks: "local-disk 50 HDD"
    }

}
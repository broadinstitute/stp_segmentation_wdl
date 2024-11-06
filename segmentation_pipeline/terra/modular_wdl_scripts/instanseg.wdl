version 1.0
task instanseg {

    input {
        Array[File] image_paths_list
        Float image_pixel_size
    }

    command <<<

        python /opt/run_instanseg.py --image_paths_list ~{sep=',' image_paths_list} \
                                --image_pixel_size ~{image_pixel_size}

    >>>

    output {
        File processed_cell_polygons = "cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/instanseg@sha256:dab6f4b4826151da462d36c6e6c5b42de53e1a01e2f91ddb5e57244fc64aa653"
        memory: "120GB"
        preemptible: 2
        cpu: 32
        disks: "local-disk 50 HDD"
    }

}
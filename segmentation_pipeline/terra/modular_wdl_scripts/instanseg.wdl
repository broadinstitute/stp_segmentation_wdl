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
        docker: "jishar7/instanseg@sha256:43651cc97bcbbd28d464ba8d2de143b9e17a8c669264a8fdbb0db37228e83459"
        memory: "120GB"
        preemptible: 2
        cpu: 32
        disks: "local-disk 50 HDD"
    }

}
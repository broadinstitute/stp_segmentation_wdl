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
        docker: "jishar7/instanseg@sha256:d5228a3456a792c0a80c64bbdc65d2f8983b0353fda5de005aef7cf3e547cd62"
        memory: "400GB"
        preemptible: 0
        cpu: 32
        disks: "local-disk 400 HDD"
    }

}
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
        docker: "jishar7/instanseg@sha256:17c8afea9c77e48bec4ffb5864b17c26cb9b07f51db5406c72cefb95f9d0176c"
        memory: "400GB"
        preemptible: 0
        cpu: 32
        disks: "local-disk 200 HDD"
    }

}
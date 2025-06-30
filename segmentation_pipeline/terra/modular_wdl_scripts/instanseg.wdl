version 1.0
task instanseg {

    input {
        Array[File]? image_paths_list
        Float? image_pixel_size
        String? technology
    }

    command <<<

        python /opt/run_instanseg.py --image_paths_list ~{sep=',' image_paths_list} \
                                --image_pixel_size ~{image_pixel_size} \
                                --technology ~{technology}

    >>>

    output {
        File processed_cell_polygons = "cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/instanseg@sha256:811a0845854e9f39be52dbeab10d40512442b8e8bd3e4f756a9570e0c197e584"
        memory: "400GB"
        preemptible: 0
        cpu: 32
        disks: "local-disk 200 HDD"
    }

}
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
        docker: "jishar7/instanseg@sha256:5fa4d3ac8a0721153c7d842b5090a601e9e4cd148193a49a8f4339dcbcf82ce8"
        memory: "120GB"
        preemptible: 2
        cpu: 32
        disks: "local-disk 50 HDD"
    }

}
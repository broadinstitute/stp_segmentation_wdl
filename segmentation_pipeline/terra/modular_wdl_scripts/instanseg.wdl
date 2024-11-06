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
        docker: "jishar7/instanseg@sha256:48cdc93a8862db3b5c43230454a49b3e323ff71a862468fd481a8a4400ce5c5b"
        memory: "120GB"
        preemptible: 2
        cpu: 32
        disks: "local-disk 50 HDD"
    }

}
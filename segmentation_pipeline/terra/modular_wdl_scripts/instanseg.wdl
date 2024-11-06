version 1.0
task instanseg {

    input {
        Array[File] image_paths_list
    }

    command <<<

        python /opt/instanseg.py --image_paths_list ~{sep=',' image_paths_list}

    >>>

    output {
        File processed_cell_polygons = "cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/instanseg@sha256:b82b9d590976e0cbd40dcd86e7d8252ca8cd7adec7654a9f90fb49b795be3aba"
        memory: "50GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
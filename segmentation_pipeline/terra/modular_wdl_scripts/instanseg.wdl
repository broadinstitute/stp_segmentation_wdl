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
        docker: "jishar7/instanseg@sha256:3fa64531976b150ae22b9854b568569cdbf7e108fd3fd5fffe9d2dcbeec8d004"
        memory: "50GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
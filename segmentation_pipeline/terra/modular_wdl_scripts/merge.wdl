version 1.0
task merge_segmentation_dfs {

    input {
        Array[Array[File]] outlines
        Array[File] outline_files = flatten(outlines)
        File intervals
    }

    command <<<

        python /opt/merge_polygons.py --cell_outlines ~{sep=',' outline_files} \
                                --intervals ~{intervals}
    >>>

    output {
        File processed_cell_polygons = "processed_cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/merge_polygons_for_terra@sha256:e92c712f66ce3870670de22d0263ea13079f77a7a9f31c864aa4a33bd2b08b9f"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
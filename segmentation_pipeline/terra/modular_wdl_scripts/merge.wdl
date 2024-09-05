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
        File processed_cell_polygons = "cell_polygons.parquet"
        File raw_cell_polygons = "raw_cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/merge_polygons_for_terra@sha256:f89edfaba40b2c029be1bfcb7f3192fc2ca9d127802a3c6aa9ae0be6e92f6d19"
        memory: "50GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
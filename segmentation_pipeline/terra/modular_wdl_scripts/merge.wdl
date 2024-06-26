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
        File merged_cell_polygons = "merged_cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/merge_polygons_for_terra@sha256:b739e11e9249b0d9a0a38fd340afc6cb7f829dc5f286509ce6f1139b25dca2d1"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
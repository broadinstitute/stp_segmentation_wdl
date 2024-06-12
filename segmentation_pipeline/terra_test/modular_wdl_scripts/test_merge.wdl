version 1.0
task merge_segmentation_dfs {

    input {
        Array[Array[File]]? outlines
        Array[File]? outline_files = flatten(outlines)
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
        docker: "jishar7/merge_polygons_for_terra@sha256:24d5a6d325ece139be60cda96653bd4bbd70e533403ac87274fce03fa217bbff"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
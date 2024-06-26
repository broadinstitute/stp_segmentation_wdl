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
        docker: "jishar7/merge_polygons_for_mac@sha256:4742bc58b1129b52a034f84530a94052e861375772048b89f9ae2d1b484795ff"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
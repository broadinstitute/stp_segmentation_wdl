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
        docker: "jishar7/merge_polygons_for_mac@sha256:cd6c0f3f886fbbbb34ed7da1418cdf7e381088ee0009d1ede2ea3f06354ddf54"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
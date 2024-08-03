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
    }

    runtime {
        docker: "jishar7/merge_polygons_for_terra@sha256:55535dbf29f9ea2525c07304f18c5a5e91f172b0d28d331bb0f7fec059d260bf"
        memory: "50GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
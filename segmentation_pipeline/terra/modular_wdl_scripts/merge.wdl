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
        docker: "jishar7/merge_polygons_for_terra@sha256:afdd8998a0b434fd2bc6e2c8c81e9a43d395f452067e1cf0865b0b13c38fa6a3"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
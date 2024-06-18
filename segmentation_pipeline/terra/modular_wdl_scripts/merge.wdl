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
        docker: "jishar7/merge_polygons_for_terra@sha256:a473c1d1581354f693dd9ee1a35cd91f1f706c4b673e668c899362653af51b6b"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
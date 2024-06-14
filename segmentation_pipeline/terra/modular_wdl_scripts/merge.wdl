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
        docker: "jishar7/merge_polygons_for_terra@sha256:e60f4ac01c85566bc6202e9711c4aebb082852d12dc47c9bf448d3d2505bd0d3"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
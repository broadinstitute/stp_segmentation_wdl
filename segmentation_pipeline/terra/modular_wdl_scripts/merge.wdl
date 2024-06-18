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
        docker: "jishar7/merge_polygons_for_terra@sha256:51881085d668b989cfeb29e3ea66d8dc4384a8a173dbf2eb5fa885b5d9002e39"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
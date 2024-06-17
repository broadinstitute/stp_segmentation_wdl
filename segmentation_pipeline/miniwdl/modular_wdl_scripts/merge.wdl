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
        docker: "jishar7/merge_polygons_for_mac@sha256:4f3bd8ecd305f140bc915b67fa2cb27319f196a58ec88cc1ac060e5169c3b519"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
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
        docker: "jishar7/merge_polygons_for_terra@sha256:da20224d423e9b3cd8ae117aa52531e0cbb7e6a55ba604cdf913c363d5ca40b1"
        memory: "50GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
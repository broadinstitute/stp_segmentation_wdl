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
        docker: "jishar7/merge_polygons_for_terra@sha256:a3108f5089ba3dd1219e7f7a4a8780c109c9990130f8431d60d5c210c0a2857c"
        memory: "50GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
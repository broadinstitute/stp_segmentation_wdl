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
        docker: "jishar7/merge_polygons_for_terra@sha256:f4d318f0020bc8be5736817af2611e3b707c849771a6471a7426b3ccd5be17d6"
        memory: "50GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
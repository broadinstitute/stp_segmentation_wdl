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
        docker: "jishar7/merge_polygons_for_mac@sha256:08b3e871b51fb6ed9d5977fedeff78e2095e17e9c68eb3cf320a8feffa99b12b"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
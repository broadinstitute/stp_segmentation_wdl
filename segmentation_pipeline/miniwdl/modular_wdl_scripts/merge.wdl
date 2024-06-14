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
        docker: "jishar7/merge_polygons_for_mac@sha256:ce2a3a7e9b0ec082987506884e25314932d9d460824fc17babccbe944f7c0843"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
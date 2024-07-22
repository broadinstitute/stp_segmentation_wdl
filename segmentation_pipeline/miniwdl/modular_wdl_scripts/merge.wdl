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
        docker: "jishar7/merge_polygons_for_mac@sha256:a68983851dc21de4a4c23157275e04da8cf0d4516201a8fc8c9cbb8445522cc1"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
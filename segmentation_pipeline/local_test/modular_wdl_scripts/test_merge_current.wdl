version 1.0
task merge_segmentation_dfs {

    input {
        Array[Array[File]]+ outlines
        File intervals
    }

    command <<<
        python /opt/merge_polygons.py --cell_outlines ~{sep=',' outlines} \
                                --intervals ~{intervals}
    >>>

    output {
        File merged_cell_polygons = "merged_cell_polygons.shp"
    }

    runtime {
        docker: "jishar7/merge_polygons@sha256:5dabe6857c69ca44547a747a60b1c124f081d07247b02da60c953862e34a08a3"
        memory: "100GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
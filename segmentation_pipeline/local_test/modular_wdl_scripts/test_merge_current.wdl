version 1.0
task merge_segmentation_dfs {

    input {
        Array[Array[File]]+ outlines
        Array[File]+ outline_files = flatten(outlines)
        File intervals
    }

    command <<<
        python /opt/merge_dfs.py --segmentation_paths ~{sep=',' segmentation_files} \
                                --segmentation_cell_stats_paths ~{sep=',' segmentation_stats_files}
    >>>

    output {
        File merged_segmentation = "merged_segmentation.csv"
        File merged_segmentation_counts = "merged_segmentation_counts.csv"
        File merged_segmentation_stats = "merged_segmentation_stats.csv"

    }

    runtime {
        docker: "oppdataanalysis/merge_segmentation@sha256:5dabe6857c69ca44547a747a60b1c124f081d07247b02da60c953862e34a08a3"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}
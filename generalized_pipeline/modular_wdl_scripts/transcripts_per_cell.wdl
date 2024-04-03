version 1.0
task get_transcripts_per_cell {

    input {
        File mask
        File detected_transcripts
        File transform
    }

    command {
       python /opt/mask_overlap.py \
       --mask ${mask} \
       --detected_transcripts ${detected_transcripts} \
       --transform ${transform} 
    }

    output {
        File detected_transcripts_cellID = "detected_transcripts_cellID.csv"
    }

    runtime {
        docker: "oppdataanalysis/image_seg_transcript:V1.0"
        memory: "20GB"
        preemptible: 2
        maxRetries: 0
        disks: "local-disk 200 HDD"
    }

}
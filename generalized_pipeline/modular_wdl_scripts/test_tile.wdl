version 1.0
task get_tile_intervals {
    input {
        File image_path
        File detected_transcripts
        File transform  
        Int ntiles_width
        Int ntiles_height
        Int overlap
    }

    command {
        python /opt/tile_intervals.py --input_image=${image_path} \
                                    --detected_transcripts=${detected_transcripts} \
                                    --transform=${transform} \
                                    --out_path="/cromwell_root/" \
                                    --ntiles_width=${ntiles_width} \
                                    --ntiles_height=${ntiles_height} \
                                    --overlap=${overlap}
    }

    output {
        File intervals = "intervals.txt"
        # File num_VMs_in_use_file = "num_VMs_in_use.txt"
    }

    runtime {
        docker: "jishar7/tiling:V9.0"
        memory: "20GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }
    
}


task get_tile {
    input {
        File image_path
        File detected_transcripts
        File transform 
		String interval
    }

    command {
        python /opt/tiling_script.py --input_image=${image_path} \
                                    --detected_transcripts=${detected_transcripts} \
                                    --transform=${transform} \
                                    --out_path="/cromwell_root/" \
                                    --interval=${interval} \
                                    --show="False"
    }

    output {
        Array[File] tile_metadata = glob("tile_metadata_*.csv")
        Array[File] tiled_image = glob("tiled_image_*.tiff")
        Array[File] tiled_detected_transcript = glob("tiled_detected_transcript_*.csv")
    }

    runtime {
        docker: "jishar7/tiling:V9.0"
        memory: "20GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }
    
}
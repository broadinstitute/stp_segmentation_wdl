version 1.0
task get_tile_intervals {
    input {
        File image_path
        File detected_transcripts
        File transform  
        Int tiles_dimension
        Int overlap
    }

    command {
        python /opt/tile_intervals.py --input_image=${image_path} \
                                    --detected_transcripts=${detected_transcripts} \
                                    --transform=${transform} \
                                    --tiles_dimension=${tiles_dimension} \
                                    --overlap=${overlap}
    }

    output {
        File intervals = "data.json"
        # File num_VMs_in_use_file = "num_VMs_in_use.txt"
    }

    runtime {
        docker: "jishar7/tiling_for_mac@sha256:a4c2e491e326c458a76b920e3013657f7f71ff18651eff3d35519dc41fc4090f"
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
		Array[String] interval
        String shard_index
    }

    command {
        python /opt/tiling_script.py --input_image=${image_path} \
                                    --detected_transcripts=${detected_transcripts} \
                                    --transform=${transform} \
                                    --out_path="$(pwd)" \
                                    --interval="~{sep=', ' interval}" \
                                    --show="False" \
                                    --shard_index=${shard_index}
    }

    output {
        Array[File] tile_metadata = glob("tile_metadata_*.csv")
        Array[File] tiled_image = glob("tiled_image_*.tiff")
        Array[File] tiled_detected_transcript = glob("tiled_detected_transcript_*.csv")
    }

    runtime {
        docker: "jishar7/tiling_for_mac@sha256:a4c2e491e326c458a76b920e3013657f7f71ff18651eff3d35519dc41fc4090f"
        memory: "20GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }
    
}
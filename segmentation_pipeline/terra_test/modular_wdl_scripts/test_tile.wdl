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
                                    --out_path="/cromwell_root/" \
                                    --tiles_dimension=${tiles_dimension} \
                                    --overlap=${overlap}
    }

    output {
        File intervals = "data.json"
        # File num_VMs_in_use_file = "num_VMs_in_use.txt"
    }

    runtime {
        docker: "jishar7/tiling_for_terra@sha256:5f47a23173e4c03ae13348f25125aea6a6c3ad39026469ac9bd6c3a8087c63ba"
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
                                    --out_path="/cromwell_root/" \
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
        docker: "jishar7/tiling_for_terra@sha256:5f47a23173e4c03ae13348f25125aea6a6c3ad39026469ac9bd6c3a8087c63ba"
        memory: "20GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }
    
}
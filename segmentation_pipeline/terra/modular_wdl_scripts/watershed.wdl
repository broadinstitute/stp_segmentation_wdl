version 1.0
task run_watershed {

    input {
        Array[File] image_files_path
        String? shard_index
    }

    command <<<

        image_paths=$(printf "%s\n" ~{sep=' ' image_files_path} | grep "tiled_image_~{shard_index}_.*\.tiff" | paste -sd "," -)

        echo "Using image paths: $image_paths"

        python /opt/watershed.py --image_paths "$image_paths"

    >>>

    output {
        Array[File] outlines = glob("*.parquet")
    }

    runtime {
        docker: "jishar7/watershed_for_terra@sha256:3eca92d7643f9b559cbd2fbab52cfb86f3e86365f77da863b14a3924309a3966"
        memory: "200GB"
        preemptible: 0
        disks: "local-disk 300 HDD"
    }

}
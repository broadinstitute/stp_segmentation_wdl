version 1.0
task run_proseg {

	input {
    	File detected_transcripts_file
        String technology
    }

    command <<<

        if [ ~{technology} == "Xenium" ]; then
            proseg ~{detected_transcripts_file} --xenium
        else
            proseg ~{detected_transcripts_file} --merscope
        fi

    >>>

    output {

        File cbg = "expected-counts.csv.gz"
        File trx_meta = "transcript-metadata.csv.gz"
        File cell_polygons = "cell-polygons.geojson.gz"

    }

    runtime {
        continueOnReturnCode: [0, 1]
        docker: "jishar7/proseg_for_terra@sha256:9e7babc7622d5e5e9d74569017005551ed7d3e4e509560740005b7c0bd2e6e21"
        memory: "400GB"
        preemptible: 2
        maxRetries: 0
        disks: "local-disk 400 HDD"

    }

}
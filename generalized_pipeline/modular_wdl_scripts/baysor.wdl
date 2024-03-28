version 1.0
task run_baysor {

    input {
        File detected_transcripts_cellID
        Int size
        Float prior_confidence
    }

	command {
       
        if [[ $(wc -l <${detected_transcripts_cellID}) -ge 2 ]];then

            # not an ideal situation but its what worked
            julia -e 'show(Sys.CPU_NAME)'
            julia -e 'using Pkg; Pkg.add(Pkg.PackageSpec(;name="PackageCompiler", version="2.0.6"))'
            printf "#!/usr/local/julia/bin/julia\n\nimport Baysor: run_cli\nrun_cli()" >> /cromwell_root/baysor && chmod +x /cromwell_root/baysor

            /cromwell_root/baysor run -x=global_x \
                -y=global_y \
                -z=global_z \
                -g=barcode_id \
                --no-ncv-estimation \
                -s=${size} \
                -m=10 \
                --prior-segmentation-confidence=${prior_confidence} \
                --save-polygons=geojson \
                --plot \
                ${detected_transcripts_cellID} ::cell

        else
            echo "too few lines in file"
            echo "too,few,lines" > segmentation.csv
            echo "too\tfew\tlines" > segmentation_counts.tsv
            echo "too,few,lines" > segmentation_cell_stats.csv
        fi
      
    }

    output {
        File baysor_out = "segmentation.csv"
        File baysor_counts = "segmentation_counts.tsv"
        File baysor_stat = "segmentation_cell_stats.csv"
    }

    runtime {
        docker: "vpetukhov/baysor:latest"
        memory: "100GB"
        maxRetries: 1
        disks: "local-disk 200 HDD"

    }
    
}

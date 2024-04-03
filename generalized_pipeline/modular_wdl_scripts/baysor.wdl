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
            julia -e 'using Pkg; Pkg.add("IJulia"); Pkg.build(); using IJulia;'
            julia -e 'using Pkg; Pkg.add(Pkg.PackageSpec(;name="PackageCompiler", version="2.0.6"))'
            julia -e 'using Pkg; Pkg.add(PackageSpec(url="https://github.com/kharchenkolab/Baysor.git")); Pkg.build();'
            julia -e 'import Baysor, Pkg; Pkg.activate(dirname(dirname(pathof(Baysor)))); Pkg.instantiate(); Pkg.build();'
            printf "#!/usr/local/julia/bin/julia\n\nimport Baysor\nBaysor.run_cli()" >> /cromwell_root/baysor && chmod +x /cromwell_root/baysor

            /cromwell_root/baysor run -x=global_x \
                -y=global_y \
                -z=global_z \
                -g=barcode_id \
                --no-ncv-estimation \
                -s=${size} \
                -m=10 \
                --prior-segmentation-confidence=${prior_confidence} \
                --save-polygons=geojson \
                ${detected_transcripts_cellID}

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
        File baysor_polygons = "segmentation_polygons.json"
    }

    runtime {
        docker: "oppdataanalysis/julia_baysor:V1.0"
        memory: "100GB"
        maxRetries: 0
        disks: "local-disk 200 HDD"

    }
    
}

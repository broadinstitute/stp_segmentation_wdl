version 1.0
task run_baysor {

    input {
        Array[File] detected_transcripts_cellID
        Int size
        Float prior_confidence
    }

	command {
       
        # not an ideal situation but its what worked
        julia -e 'show(Sys.CPU_NAME)'
        julia -e 'using Pkg; Pkg.add("IJulia"); Pkg.build(); using IJulia;'
        julia -e 'using Pkg; Pkg.add(Pkg.PackageSpec(;name="PackageCompiler", version="2.0.6"))'
        julia -e 'using Pkg; Pkg.add(PackageSpec(url="https://github.com/kharchenkolab/Baysor.git")); Pkg.build();'
        julia -e 'import Baysor, Pkg; Pkg.activate(dirname(dirname(pathof(Baysor)))); Pkg.instantiate();'
        printf "#!/usr/local/julia/bin/julia\n\nimport Baysor: run_cli\nrun_cli()" >> /cromwell_root/baysor && chmod +x /cromwell_root/baysor
        
        index=0
        for value in $detected_transcripts_cellID;

        do
        
        /cromwell_root/baysor run -x=global_x \
            -y=global_y \
            -z=global_z \
            -g=barcode_id \
            --no-ncv-estimation \
            -s=${size} \
            -m=10 \
            --prior-segmentation-confidence=${prior_confidence} \
            --save-polygons=geojson \
            ${value}
        
        mv segmentation.csv "segmentation_${index}.csv"
        mv segmentation_counts.tsv "segmentation_counts_${index}.tsv"  
        mv segmentation_cell_stats.csv "segmentation_cell_stats_${index}.csv"
        mv segmentation_polygons.json "segmentation_polygons_${index}.json"

        done
      
    }

    output {

        Array[File] baysor_out = glob("segmentation_*.csv")
        Array[File] baysor_counts = glob("segmentation_counts_*.tsv")
        Array[File] baysor_stat = glob("segmentation_cell_stats_*.csv")
        Array[File] baysor_polygons = glob("segmentation_polygons_*.json")

    }

    runtime {
        docker: "vpetukhov/baysor:latest"
        memory: "100GB"
        maxRetries: 0
        disks: "local-disk 200 HDD"

    }
    
}

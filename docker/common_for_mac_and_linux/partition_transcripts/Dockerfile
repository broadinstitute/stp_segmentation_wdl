FROM python:3.9

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gdal-bin \
    libspatialindex-dev \
    libgdal-dev \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pandas==2.2.2
RUN pip install geopandas==0.14.4
RUN pip install google-cloud-storage==2.17.0
RUN pip install shapely==2.0.4
RUN pip install numpy==1.26.4
RUN pip install argparse==1.4.0
RUN pip install pyarrow==16.1.0
RUN pip install fastparquet==2024.5.0

COPY common_python_scripts/partition_transcripts.py /opt/partition_transcripts.py
RUN chmod +x /opt/partition_transcripts.py

ENTRYPOINT ["/bin/bash", "-l", "-c", "/bin/bash"]
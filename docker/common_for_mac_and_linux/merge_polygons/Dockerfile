FROM python:3.9

RUN apt-get update && \
    apt-get install -y libgdal-dev && \
    apt-get install -y --no-install-recommends \
    gdal-bin \
    python3-gdal \
    libspatialindex-dev \
    build-essential \
    python3-dev \
    libc6-dev \
    libgeos-c1v5 \
    libgeos-dev \
    libproj-dev \
    proj-bin \
    proj-data \
    libspatialite-dev \
    libsqlite3-mod-spatialite \
    sqlite3 \
    libsqlite3-dev \
    wget \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install required Python packages
RUN pip install --no-cache-dir pandas==2.2.2
RUN pip install geopandas==0.14.4
RUN pip install google-cloud-storage==2.17.0
RUN pip install shapely==2.0.4
RUN pip install matplotlib==3.9.0
RUN pip install argparse==1.4.0
RUN pip install pyarrow==16.1.0
RUN pip install fastparquet==2024.5.0

COPY common_python_scripts/merge_polygons.py /opt/merge_polygons.py
RUN chmod +x /opt/merge_polygons.py

ENTRYPOINT ["/bin/bash", "-l", "-c", "/bin/bash"]
FROM python:3.9

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gdal-bin \
    python3-gdal \
    libspatialindex-dev \
    libgdal-dev \
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
RUN pip install --no-cache-dir pandas geopandas google-cloud-storage shapely matplotlib argparse pyarrow fastparquet

COPY merge_polygons.py /opt/merge_polygons.py
RUN chmod +x /opt/merge_polygons.py

ENTRYPOINT ["/bin/bash", "-l", "-c", "/bin/bash"]
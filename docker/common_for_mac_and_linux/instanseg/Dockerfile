# Base image with Python 3.10 for compatibility
FROM python:3.10

# Install system dependencies for geospatial and image processing libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libspatialindex-dev \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    torch==2.5.1 \
    tifffile==2024.9.20 \
    imagecodecs==2024.9.22 \
    aicsimageio==4.11.0 \
    instanseg-torch[full]==0.0.5 \
    fastremap==1.15.0 \
    scikit-image==0.22.0 \
    shapely==2.0.6 \
    geopandas==1.0.1 \
    bioio==1.1.0 \
    bioio-ome-tiff \
    bioio-ome-zarr \
    pyarrow==16.1.0 \
    fastparquet==2024.5.0 \
    ujson

COPY common_python_scripts/run_instanseg.py /opt/run_instanseg.py
RUN chmod +x /opt/run_instanseg.py

ENTRYPOINT ["/bin/bash", "-l", "-c", "/bin/bash"]
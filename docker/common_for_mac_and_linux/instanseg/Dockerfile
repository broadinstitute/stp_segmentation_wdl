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
    numpy \
    torch \
    tifffile \
    imagecodecs \
    aicsimageio \
    instanseg \
    bioio \
    fastremap \
    scikit-image \
    shapely \
    geopandas

COPY common_python_scripts/instanseg.py /opt/instanseg.py
RUN chmod +x /opt/instanseg.py

ENTRYPOINT ["/bin/bash", "-l", "-c", "/bin/bash"]
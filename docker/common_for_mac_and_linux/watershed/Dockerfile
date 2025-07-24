FROM python:3.9

# Install system dependencies
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
    ca-certificates \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    pandas==2.2.2 \
    geopandas==0.14.4 \
    shapely==2.0.4 \
    matplotlib==3.9.0 \
    argparse==1.4.0 \
    pyarrow==16.1.0 \
    fastparquet==2024.5.0 \
    opencv-python-headless==4.8.0.76 \
    numpy \
    scikit-image \
    tifffile \
    scipy

# Copy your watershed segmentation script into the container
COPY common_python_scripts/watershed.py /opt/watershed.py
RUN chmod +x /opt/watershed.py

# Set working directory
WORKDIR /opt

# Entrypoint (run the script by default)
ENTRYPOINT ["python", "/opt/watershed.py"]

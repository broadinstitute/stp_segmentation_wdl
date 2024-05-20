FROM python:3.8.16
RUN apt-get update && apt-get install -y gdal-bin libgdal-dev
RUN pip3 install fiona
RUN pip3 install matplotlib pandas numpy argparse scikit-image shapely geopandas rtree
RUN pip install pyarrow fastparquet  # Add this line to install pyarrow and fastparquet
COPY mask_overlap.py /opt/mask_overlap.py
RUN chmod +x /opt/mask_overlap.py
#CMD ["/bin/sh" "-c" "echo \"This is a test.\" | wc -"]
ENTRYPOINT ["/bin/sh", "-c", "/bin/bash"]

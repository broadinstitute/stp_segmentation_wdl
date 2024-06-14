FROM python:3.8.16
RUN apt-get update && apt-get install -y gdal-bin libgdal-dev

RUN pip3 install fiona==1.9.6
RUN pip3 install matplotlib==3.9.0
RUN pip3 install pandas==2.2.2
RUN pip3 install numpy==1.26.4
RUN pip3 install argparse==1.4.0
RUN pip3 install scikit-image==0.23.2
RUN pip3 install shapely==2.0.4
RUN pip3 install geopandas==0.14.4
RUN pip3 install rtree==1.2.0
RUN pip install pyarrow==16.1.0 
RUN pip install fastparquet==2024.5.0

COPY mask_overlap.py /opt/mask_overlap.py
RUN chmod +x /opt/mask_overlap.py
#CMD ["/bin/sh" "-c" "echo \"This is a test.\" | wc -"]
ENTRYPOINT ["/bin/sh", "-c", "/bin/bash"]

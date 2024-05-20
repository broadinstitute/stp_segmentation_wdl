FROM python:3.8.16

RUN apt-get update \
    && apt-get install -y python3-opencv

RUN pip3 install opencv-python
RUN pip3 install numpy tifffile matplotlib pandas seaborn argparse
COPY tiling_script.py /opt/tiling_script.py
COPY utils.py /opt/utils.py
COPY tile_intervals.py /opt/tile_intervals.py
RUN chmod +x /opt/tiling_script.py
RUN chmod +x /opt/tile_intervals.py
CMD ["/bin/sh" "-c" "echo \"This is a test.\" | wc -"]
ENTRYPOINT ["/bin/sh", "-c", "/bin/bash"]

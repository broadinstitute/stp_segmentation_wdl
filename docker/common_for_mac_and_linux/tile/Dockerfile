FROM python:3.9

RUN pip install opencv-python==4.10.0.82
RUN pip install numpy==1.26.4
RUN pip install tifffile==2024.5.22 
RUN pip install matplotlib==3.9.0
RUN pip install pandas==2.2.2
RUN pip install seaborn==0.13.2 
RUN pip install argparse==1.4.0

COPY common_python_scripts/tiling_script.py /opt/tiling_script.py
COPY common_python_scripts/utils.py /opt/utils.py
COPY common_python_scripts/tile_intervals.py /opt/tile_intervals.py

RUN chmod +x /opt/tiling_script.py
RUN chmod +x /opt/tile_intervals.py
CMD ["/bin/sh" "-c" "echo \"This is a test.\" | wc -"]
ENTRYPOINT ["/bin/sh", "-c", "/bin/bash"]
FROM python:3.9

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

RUN pip install numpy==1.26.4
RUN pip install opencv-python==4.10.0.82
RUN pip install tifffile==2024.5.22 
RUN pip install pandas==2.2.2
RUN pip install argparse==1.4.0
RUN pip install pyarrow==16.1.0

COPY common_python_scripts/create_subset.py /opt/create_subset.py

RUN chmod +x /opt/create_subset.py
CMD ["/bin/sh" "-c" "echo \"This is a test.\" | wc -"]
ENTRYPOINT ["/bin/sh", "-c", "/bin/bash"]
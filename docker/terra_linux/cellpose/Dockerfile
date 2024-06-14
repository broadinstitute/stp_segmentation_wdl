FROM python:3.9

USER root
ENV PIP_USER=false
RUN apt-get update \
    && apt-get install -yq --no-install-recommends   python-tk   tk-dev   libssl-dev   xz-utils   libhdf5-dev   openssl   make   liblzo2-dev   zlib1g-dev   libz-dev   libglu1-mesa   libcurl4-openssl-dev   \
    && apt-get clean   \
    && rm -rf /var/lib/apt/lists/*
RUN pip install cellpose==3.0.9
RUN pip install scikit-image==0.23.2
RUN pip install opencv-python==4.10.0.82
RUN pip install matplotlib==3.9.0
RUN pip install numpy==1.26.4

ENTRYPOINT ["/bin/bash", "-l", "-c", "/bin/bash"]
FROM python:3.8.5

USER root
ENV PIP_USER=false
RUN apt-get update \
    && apt-get install -yq --no-install-recommends   python-tk   tk-dev   libssl-dev   xz-utils   libhdf5-dev   openssl   make   liblzo2-dev   zlib1g-dev   libz-dev   libglu1-mesa   libcurl4-openssl-dev   \
    && apt-get clean   \
    && rm -rf /var/lib/apt/lists/*
RUN pip install cellpose
RUN pip install scikit-image
RUN pip install opencv-python
RUN pip install matplotlib
RUN pip install numpy==1.23
ENTRYPOINT ["/bin/bash", "-l", "-c", "/bin/bash"]

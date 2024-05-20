FROM python:3.9

RUN apt-get update && apt-get install -yq --no-install-recommends \
    tk-dev \
    libssl-dev \
    xz-utils \
    libhdf5-dev \
    openssl \
    make \
    liblzo2-dev \
    zlib1g-dev \
    libz-dev \
    libglu1-mesa \
    libgl1-mesa-glx \
    libcurl4-openssl-dev \
    python3-tk \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install --verbose cellpose
RUN pip install scikit-image
RUN pip install opencv-python
RUN pip install matplotlib
RUN pip install numpy==1.23
ENTRYPOINT ["/bin/bash", "-l", "-c", "/bin/bash"]
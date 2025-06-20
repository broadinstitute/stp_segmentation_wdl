FROM python:3.11.5

RUN mv /etc/apt/apt.conf.d/docker-clean /etc/apt/apt.conf.d/docker-clean-disabled

RUN apt-get update --allow-insecure-repositories && \
    apt-get install -y --no-install-recommends \
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

RUN mv /etc/apt/apt.conf.d/docker-clean-disabled /etc/apt/apt.conf.d/docker-clean

RUN pip install --upgrade pip
RUN pip install --verbose cellpose==4.0.4
RUN pip install scikit-image==0.23.2
RUN pip install opencv-python==4.10.0.82
RUN pip install matplotlib==3.9.0
RUN pip install numpy==1.26.4

ENTRYPOINT ["/bin/bash", "-l", "-c", "/bin/bash"]
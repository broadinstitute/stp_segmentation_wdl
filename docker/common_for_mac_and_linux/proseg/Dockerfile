FROM python:3.10

# Disable Docker's default apt clean-up behavior temporarily
RUN mv /etc/apt/apt.conf.d/docker-clean /etc/apt/apt.conf.d/docker-clean-disabled

# Install system dependencies
RUN apt-get update --allow-insecure-repositories && \
    apt-get install -y --no-install-recommends \
    curl \
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
    build-essential \
    pkg-config \
&& apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Restore Docker's apt clean-up behavior
RUN mv /etc/apt/apt.conf.d/docker-clean-disabled /etc/apt/apt.conf.d/docker-clean

# Install Rust (non-interactive)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Ensure cargo is in the PATH for all future steps
ENV PATH="/root/.cargo/bin:${PATH}"

# Install proseg using cargo
RUN cargo install proseg && \
    proseg --help

# Install Python dependencies
RUN pip install --upgrade pip==24.0

ENTRYPOINT ["/bin/bash", "-l", "-c", "/bin/bash"]

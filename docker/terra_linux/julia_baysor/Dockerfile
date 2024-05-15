FROM julia:1.8.3
RUN apt-get update \
    && apt-get install -y build-essential
RUN apt-get install -y gfortran
RUN apt-get install -y python3 python3-pip vim git wget
RUN pip3 install jupyterlab numpy scipy matplotlib seaborn pandas sklearn scikit-image
RUN pip3 install -Iv six==1.12.0
ENTRYPOINT ["/bin/bash"]
FROM julia:1.8.3
RUN apt-get update \
    && apt-get install -y build-essential
RUN apt-get install -y gfortran
RUN apt-get install -y python3 python3-pip vim git wget

RUN pip3 install jupyterlab==4.2.2
RUN pip3 install numpy==1.26.4
RUN pip3 install scipy==1.13.1 
RUN pip3 install matplotlib==3.9.0
RUN pip3 install seaborn==0.13.2 
RUN pip3 install pandas==2.2.2
RUN pip3 install scikit-learn==1.5.0
RUN pip3 install scikit-image==0.23.2

RUN pip3 install -Iv six==1.12.0
ENTRYPOINT ["/bin/bash"]
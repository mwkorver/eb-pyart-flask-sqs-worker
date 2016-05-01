# Py-Art and GDAL install, for demo testing only
FROM ubuntu:14.04
MAINTAINER Mark Korver<mwkorver@gmail.com>

# System packages 
RUN apt-get update && apt-get install -y curl wget git gcc gdal-bin

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
RUN bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

# Python packages from conda
RUN conda install --yes \
    flask \
    boto

# Install Py-ART dependencies
RUN conda install --yes \
    numpy \
    scipy \
    matplotlib \
    netcdf4 

RUN conda install --yes -c http://conda.anaconda.org/jjhelmus trmm_rsl

# Dependency on Ubuntu for Matplotlib
RUN apt-get install -y python-qt4

# Optional Py-ART dependencies
RUN conda install --yes \
    basemap \
    pyproj \
    nose \
    gdal

RUN git clone https://github.com/ARM-DOE/pyart.git &&\
    cd pyart &&\
    python setup.py install &&\
    cd ../

# Install AWS CLI for debugging purposes
# RUN pip install awscli


RUN wget http://github.com/mwkorver/eb-pyart-flask-sqs-worker/archive/master.zip -O temp.zip &&\
   unzip temp.zip &&\
   rm temp.zip &&\
   cd ./eb-pyart-flask-sqs-worker &&\
   python application.py &

EXPOSE 22 5000

ENV LANG C.UTF-8

CMD [ "/bin/bash" ]
#ENTRYPOINT ["python"]
#CMD ["server.py"]

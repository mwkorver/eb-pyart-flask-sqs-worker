# Run Py-Art and GDAL to run as a Flask application. For testing only.
FROM ubuntu:14.04
MAINTAINER Mark Korver<mwkorver@gmail.com>

# System packages 
RUN apt-get update && apt-get install -y curl wget git gcc gdal-bin

# Install minicond
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh &&\
    bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b &&\
    rm Miniconda-latest-Linux-x86_64.sh  
ENV PATH=/miniconda/bin:${PATH}

# Python packages from conda
RUN conda install --yes \
    flask \
    gunicorn \
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

# Install Py-Art from source
RUN git clone https://github.com/ARM-DOE/pyart.git &&\
    cd pyart &&\
    python setup.py install &&\
    cd ../

# Update conda packages
RUN conda update -y conda


# Install AWS CLI for debugging purposes
# RUN pip install awscli

ADD application.py application.py 
ADD default_config.py default_config.py  

#CMD python application.py &

EXPOSE 22 5000

ENV LANG C.UTF-8

CMD [ "/bin/bash" ]
ENTRYPOINT ["python"]
#CMD ["application.py"]
#CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

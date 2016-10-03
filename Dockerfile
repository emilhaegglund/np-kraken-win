FROM ubuntu:14.04

RUN apt-get -y update && apt-get install -y git

RUN apt-get install --fix-missing -y wget libpng-dev \

	freetype* \

	libblas-dev \

	liblapack-dev \

	libatlas-base-dev \
	
	gfortran \

	g++\

	build-essential \

	gzip \


RUN apt-get install -y python python-pip python-dev python-setuptools python-numpy python-matplotlib python-pandas

RUN apt-get install -y libhdf5-serial-dev hdf5-tools pkg-config

RUN pip install cython

RUN pip install h5py

#Install Jellyfish V1
RUN wget http://www.cbcb.umd.edu/software/jellyfish/jellyfish-1.1.11.tar.gz && \
 tar -xzf jellyfish-1.1.11.tar.gz && \
 rm jellyfish-1.1.11.tar.gz && \
 cd jellyfish-1.1.11 && \
 ./configure && \
 make && \
 make install

#Install Kraken
RUN wget https://github.com/DerrickWood/kraken/archive/v0.10.5-beta.tar.gz && \
 tar -xzf v0.10.5-beta.tar.gz && \
 rm v0.10.5-beta.tar.gz && \
 cp jellyfish-1.1.11/bin/jellyfish kraken-0.10.5-beta && \
 cd kraken-0.10.5-beta && \
 ./install_kraken.sh . || echo "ok"
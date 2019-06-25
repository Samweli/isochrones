FROM ubuntu:trusty


#opting for ubuntugis-unstable for postgis 2.1.3 and qgis 2.6

RUN echo "deb http://qgis.org/debian trusty main" >> /etc/apt/sources.list
RUN echo "deb http://ppa.launchpad.net/ubuntugis/ubuntugis-unstable/ubuntu trusty main" >> /etc/apt/sources.list
RUN apt-get update -y

RUN apt-get install -y \
    build-essential \
    xvfb \
    git \
    python-pip \
    xvfb \
    python-nose \
    python-coverage \
    pyflakes \
    python-nosexcover \
    python-scientific

RUN pip install pep8 pylint

ENV QGIS_PREFIX_PATH /usr
ENV PYTHONPATH=${QGIS_PREFIX_PATH}/share/qgis/python/:${QGIS_PREFIX_PATH}/share/qgis/python/plugins:`pwd`
ENV LD_LIBRARY_PATH ${QGIS_PREFIX_PATH}/share/qgis/python/plugins/
ENV LD_LIBRARY_PATH ${QGIS_PREFIX_PATH}/lib

RUN apt-get install -y --force-yes postgresql-9.3-postgis-2.1 qgis
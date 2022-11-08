#!/usr/bin/env bash

QGIS_IMAGE=qgis/qgis

QGIS_VERSION_TAG=latest

export ON_TRAVIS=false
export MUTE_LOGS=true
export WITH_PYTHON_PEP=true
export QGIS_VERSION_TAG=latest
export IMAGE=qgis/qgis

DISPLAY=${DISPLAY:-:99}

if [ "${DISPLAY}" != ":99" ]; then
    xhost +
fi

IMAGES=($QGIS_IMAGE)


for IMAGE in "${IMAGES[@]}"
do
    echo "Running tests for $IMAGE"
    docker-compose up -d

    sleep 10

    # Run the real test
    time docker-compose exec -T qgis-testing-environment sh -c "qgis_testrunner.sh test_suite.test_package"

done



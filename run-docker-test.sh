#!/usr/bin/env bash

QGIS_IMAGE_V_3_0=samtwesa/qgis-testing-environment-docker:release-3_0
QGIS_IMAGE_V_3_2=samtwesa/qgis-testing-environment-docker:release-3_2
QGIS_IMAGE_V_3_4=qgis/qgis:release-3_4
QGIS_IMAGE_V_3_6=qgis/qgis:release-3_6
QGIS_IMAGE_V_3_8=qgis/qgis:final-3_8_0
QGIS_IMAGE_master=qgis/qgis:master

QGIS_VERSION_TAG=release-3_0

DISPLAY=${DISPLAY:-:99}

if [ "${DISPLAY}" != ":99" ]; then
    xhost +
fi

IMAGES=(
        $QGIS_IMAGE_V_3_4)


for IMAGE in "${IMAGES[@]}"
do
    echo "Running tests for $IMAGE"

    docker run -d --name qgis-testing-environment \
    -v ${PWD}:/tests_directory \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e WITH_PYTHON_PEP=false \
    -e ON_TRAVIS=false \
    -e MUTE_LOGS=true \
    -e DISPLAY=${DISPLAY} \
    ${IMAGE}

    sleep 10

    docker exec -it qgis-testing-environment sh -c "qgis_setup.sh isochrones"

    # FIX default installation because the sources must be in "isochrones" parent folder
    docker exec -it qgis-testing-environment sh -c "rm -f  /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones"
    docker exec -it qgis-testing-environment sh -c "ln -s /tests_directory/ /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones"
    # docker exec -it qgis-testing-environment sh -c "apt update"
    # docker exec -it qgis-testing-environment sh -c "apt install wget"
    # docker exec -it qgis-testing-environment sh -c "wget https://bootstrap.pypa.io/get-pip.py"
    # docker exec -it qgis-testing-environment sh -c "python get-pip.py"
    # docker exec -it qgis-testing-environment sh -c "pip install pydevd-pycharm~=191.6605.12"
    # Run the real test
    time docker exec -it qgis-testing-environment sh -c "qgis_testrunner.sh test_suite.test_package"

    docker kill qgis-testing-environment
    docker rm qgis-testing-environment

done



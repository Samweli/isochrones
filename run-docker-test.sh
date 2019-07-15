#!/usr/bin/env bash
IMAGE=qgis/qgis
QGIS_VERSION_TAG=release-3_4

DISPLAY=${DISPLAY:-:99}

if [ "${DISPLAY}" != ":99" ]; then
    xhost +
fi

docker run -d --name qgis-testing-environment \
    -v ${PWD}:/tests_directory \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e WITH_PYTHON_PEP=false \
    -e ON_TRAVIS=false \
    -e MUTE_LOGS=true \
    -e DISPLAY=${DISPLAY} \
    ${IMAGE}:${QGIS_VERSION_TAG}


sleep 10

docker exec -it qgis-testing-environment sh -c "qgis_setup.sh isochrones"

# FIX default installation because the sources must be in "isochrones" parent folder
docker exec -it qgis-testing-environment sh -c "rm -f  /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones"
docker exec -it qgis-testing-environment sh -c "ln -s /tests_directory/ /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones"

# Run the real test
time docker exec -it qgis-testing-environment sh -c "qgis_testrunner.sh test_suite.test_package"

docker kill qgis-testing-environment
docker rm qgis-testing-environment
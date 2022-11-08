#!/usr/bin/env bash

qgis_setup.sh

# FIX default installation because the sources must be in "isochrones" parent folder
rm -rf  /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones
ln -sf /tests_directory /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/isochrones
ln -sf /tests_directory /usr/share/qgis/python/plugins/isochrones
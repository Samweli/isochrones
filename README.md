Isochrones Qgis Plugin
=======

![Tests](https://github.com/samweli/isochrones/actions/workflows/test.yaml/badge.svg)


QGIS plugin that creates isochrones map from the given data and parameters.

![Isochrones map](resources/img/examples/isochrone.png)

## Installation

Install QGIS. Download it from this link (http://download.qgis.org/). Instructions on installing QGIS for 
different OS is available here [https://www.qgis.org/en/site/forusers/download.html#tab1](https://www.qgis.org/en/site/forusers/download.html#tab1)

### Install from QGIS plugin repository

- Launch QGIS application and open plugin manager.
- Search for `Isochrones` in the All page of the plugin manager.
- From the found results, click on the `Isochrones` result item and a page with plugin information will show up.
     ![Isochrones result item](resources/img/examples/isochrones_plugin_result.png)
- Click the `Install Plugin` button at the bottom of the dialog to install the plugin.

After a successful install the plugin will be added to your plugins menu and database menu.

### Install from a ZIP file
- Get the plugin ZIP file from https://github.com/samweli/isochrones/releases, 
  select the required release ZIP file and download it. 
- From the `Install from ZIP` page in the QGIS plugin manager, 
  select the downloaded ZIP file and click the `Install Plugin` button to install it.

![Install from zip option](resources/img/examples/install_from_zip.png)

### Install from source code

- Download or clone this repository and add the plugin folder into the QGIS plugin directory.
The plugin directory is found on the QGIS profile folder under `profile_name/plugins`,
 eg. `default/plugins`.
 
  QGIS active profile folder can be found by going to **User Profiles > Open Active Profile Folder**
    ![Active Profile folder](resources/img/examples/active_user_folder.png)

- Restart your Qgis, go to **Plugins -> Manage and Install Plugins** search for `Isochrones` 
- Search results will show a result item with `Isochrones` title, toggle the checkbox beside the title to 
  activate the plugin.

### Requirements

Postgres Database with version 9.5 or above, 
with [Postgis](https://postgis.net)(`tested with version 3.1`) and 
[pgRouting](https://pgrouting.org) (`tested with version 3.1.3`)
extensions installed.


### How to

#### Running

##### Step 1
- Setup two postgresql tables one for the network and other for the catchments areas.

- Use test data is found here
  [https://github.com/Samweli/isochrones_plugin/tree/master/iso/test/data](https://github.com/Samweli/isochrones_plugin/tree/master/iso/test/data)
  these are shapefiles that you will need to import in your postgresql database as tables.


##### Step 2

- Make note of the important columns that will be needed when using the plugin, 
  this includes the unique identifier and geometric column for both tables.
- The network data is required to have a column with a name `cost` and a number type, this will be used 
  for the path calculations during isochrones creation.
- Open the plugin (it will be on the Database Menu and the QGIS toolbar) and fill the connection details followed by tables details. 
- Checking the "Create isochrones map style" twill generate tin and contour with a default plugin style.


You can watch the demo video here [https://www.youtube.com/watch?v=thBKETlQbqY](https://www.youtube.com/watch?v=thBKETlQbqY)


#### Data

The network data before imported in the database should be prepared for routing, information on doing this can be found 
here [http://www.bostongis.com/PrinterFriendly.aspx?content_name=pgrouting_osm2po_1](http://www.bostongis.com/PrinterFriendly.aspx?content_name=pgrouting_osm2po_1) 

## Licence

Isochrones is a free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 2 (GPLv2) as published by the Free Software Foundation.

The full GNU General Public License is available in LICENSE.txt or http://www.gnu.org/licenses/gpl.html



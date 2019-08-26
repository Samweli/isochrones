Isochrones Qgis Plugin
=======

| QGIS 3.0          | QGIS 3.2          | QGIS 3.4 (LTR)    | QGIS 3.6          | QGIS 3.8          |
|-------------------|-------------------|-------------------|-------------------|-------------------|
| [![Build1][1]][7] | [![Build2][2]][7] | [![Build3][3]][7] | [![Build4][4]][7] | [![Build5][5]][7] |

[1]: https://travis-matrix-badges.herokuapp.com/repos/Samweli/isochrones/branches/master/1
[2]: https://travis-matrix-badges.herokuapp.com/repos/Samweli/isochrones/branches/master/2
[3]: https://travis-matrix-badges.herokuapp.com/repos/Samweli/isochrones/branches/master/3
[4]: https://travis-matrix-badges.herokuapp.com/repos/Samweli/isochrones/branches/master/4
[5]: https://travis-matrix-badges.herokuapp.com/repos/Samweli/isochrones/branches/master/5
[6]: https://travis-matrix-badges.herokuapp.com/repos/Samweli/isochrones/branches/master/6
[7]: https://travis-ci.org/Samweli/isochrones


Simple Plugin that creates isochrones map from the given data and parameters.

<img src="https://raw.githubusercontent.com/Samweli/isochrones_plugin/master/resources/img/examples/isochrone.png" width="600" height="500" alt="Isochrone example" />


## Installation

Install QGIS. Download it from this link (http://download.qgis.org/).

After installation of QGIS use the plugin manager: Plugins -> Manage and Install Plugins

Search for "isochrones", click the install button. It will be added to your plugins menu and database menu.

### Install from source code

Download or clone this repository and put the root folder in your
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins

and restart your Qgis, go to Plugins -> Manage and Install Plugins search for it and click it

to activate it.

Currently uploading this plugin to Qgis Plugins repository, soon you will be able to install it directly
from there.

The master branch contains latest version of this plugin.

### Requirements

Postgres Database with version 9.5 or above, with [Postgis](https://postgis.net) and [pgRouting](https://pgrouting.org) extensions installed.


### How to

#### Running

##### Step 1
You need to have two postgresql tables one for the network and other for the catchments areas.

You can use test data found [here](https://github.com/Samweli/isochrones_plugin/tree/master/iso/test/data) these are shapefiles
that you will need to import in your postgresql database as tables.


##### Step 2

Make note of the important columns that will be needed when using the plugin, this include the unique identifier and 
geometric column for both tables.

Start the plugin (it will be on the Database Menu) and fill the connection details followed by tables details.

If you check the "Create isochrones map style" this will generate tin and contour with a default style.


You can watch the demo video [here](https://www.youtube.com/watch?v=thBKETlQbqY)


#### Data

The network data before imported in the database should be prepared for routing, information on doing this can be found 
[here](http://www.bostongis.com/PrinterFriendly.aspx?content_name=pgrouting_osm2po_1) 

## Licence

Isochrones is a free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 2 (GPLv2) as published by the Free Software Foundation.

The full GNU General Public License is available in LICENSE.txt or http://www.gnu.org/licenses/gpl.html
Isochrones Qgis Plugin
=======

Simple Plugin that creates isochrones map from the given data and parameters.

<img src="https://raw.githubusercontent.com/Samweli/isochrones_plugin/master/resources/img/examples/isochrone.png" width="600" height="500" alt="Isochrone example" />


## Installation

Download or clone this repository and put the root folder in your ~/.qgis2/python/plugins

and restart your Qgis, go to Plugins -> Manage and Install Plugins search for it and click it

to activate it.

Currently uploading this plugin to Qgis Plugins repository, soon you will be able to install it directly
from there.


### Dependencies

Postgres Database with Postgis and Pgrouting extensions installed.

python-psycopg2 installed to be able to connect to the database.


### How to

#### Running

##### Step 1
You need to have two postgresql tables one for the network and other for the catchments areas.

You can use test data found [here](https://raw.githubusercontent.com/Samweli/isochrones_plugin/master/iso/test/data) these are shapefiles
that you will need to import in your postgresql database as tables.


##### Step 2

Make note of the important columns that will be needed when using the plugin, this include the unique identifier and 
geometric column for both tables.

Start the plugin (it will be on the Database Menu) and fill the connection details followed by tables details.

If you check the "Create isochrones map style" this will generate tin and contour with a default style.


#### Data

The network data before imported in the database should be prepared for routing, information on doing this can be found [here](http://www.bostongis.com/PrinterFriendly.aspx?content_name=pgrouting_osm2po_1) 



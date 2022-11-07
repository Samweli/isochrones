# -*- coding: utf-8 -*-
"""
/***************************************************************************
 database queries
                                 A QGIS plugin
 This plugin create isochrones maps.
                             -------------------
        begin                : 2016-07-02
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Samweli Mwakisambwe
        email                : smwakisambwe@worldbank.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from builtins import str
import re

from utils import display_warning_message_box

from i18n import tr

from common.exceptions import IsochroneDBError


def create_network_view(
        connection,
        cursor,
        arguments,
        dialog,
        progress_dialog):
    """Create network view, to improve performance of queries using it

    :param connection: Database connection
    :type connection:

    :param cursor: Database connection cursor
    :type cursor:

    :param arguments: List of required parameters in
     querying the database
    :type arguments: {}

    :param dialog: Dialog attached to this method
    :type dialog: Qdialog

    :param progress_dialog: Progress dialog
    :type progress_dialog: Qdialog

    """

    progress_dialog.setValue(0)
    label_text = tr("Creating network view table")
    progress_dialog.setLabelText(label_text)

    drop_network_cache(connection, cursor, arguments, dialog)

    try:
        sql = """ CREATE OR REPLACE VIEW network_cache as
            SELECT *, _pgr_startpoint(%(network_geom)s),
            _pgr_endpoint(%(network_geom)s) FROM %(network_table)s
            """ % arguments

        sql = clean_query(sql)

        cursor.execute(sql)
        connection.commit()

    except Exception as exception:
        message = "Error in creating network view \n {}". \
            format(str(exception))

        display_warning_message_box(
            dialog, "Error",
            message
        )

        raise IsochroneDBError


def create_nodes(connection, cursor, arguments, dialog):
    """Create network nodes, this will help in creating
       a sql routable network table

    :param connection: Database connection
    :type connection:

    :param cursor: Database connection cursor
    :type cursor:

    :param arguments: List of required parameters in
     querying the database
    :type arguments: {}

    :param dialog: Dialog attached to this method
    :type dialog: Qdialog

    """
    try:

        drop_table(connection, cursor, "nodes")

        sql = """CREATE TABLE IF NOT EXISTS nodes AS
               SELECT row_number() OVER (ORDER BY foo.p)::integer AS id,
               foo.p AS the_geom
               FROM (
               SELECT DISTINCT network_cache._pgr_startpoint AS p
                FROM network_cache
               UNION
               SELECT DISTINCT network_cache._pgr_endpoint AS p
               FROM network_cache
               ) foo
               GROUP BY foo.p"""
        sql = clean_query(sql)

        cursor.execute(sql)
        connection.commit()
    except Exception as exception:
        message = "Error in creating network nodes \n {}". \
                  format(str(exception))

        display_warning_message_box(
            dialog, "Error",
            message
        )

        raise IsochroneDBError


def create_routable_network(connection, cursor, arguments, dialog):
    """Create routable network using the network view with the nodes.
       This takes long time to complete.

    :param connection: Database connection
    :type connection:

    :param cursor: Database connection cursor
    :type cursor:

    :param arguments: List of required parameters in
     querying the database
    :type arguments: {}

    :param dialog: Dialog attached to this method
    :type dialog: Qdialog

    """

    try:
        drop_table(connection, cursor, "routable_network")

        sql = """CREATE TABLE IF NOT EXISTS routable_network AS
               SELECT a.*, b.id as start_id, c.id as end_id FROM
               network_cache
               AS a
               JOIN nodes AS b ON a._pgr_startpoint = b.the_geom JOIN
               nodes AS c
               ON  a._pgr_endpoint = c.the_geom """
        sql = clean_query(sql)

        cursor.execute(sql)
        connection.commit()
    except Exception as exception:
        message = "Error in creating routable network \n {}". \
            format(str(exception))

        display_warning_message_box(
            dialog, "Error",
            message
        )

        raise IsochroneDBError


def update_catchment(connection, cursor, arguments, dialog):
    """Calculating the nearest nodes to the catchment areas,
       these nodes will be used in accessibility calculations.

    :param connection: Database connection
    :type connection:

    :param cursor: Database connection cursor
    :type cursor:

    :param arguments: List of required parameters in
     querying the database
    :type arguments: {}

    :param dialog: Dialog attached to this method
    :type dialog: Qdialog

    """

    try:
        update_catchment_table(connection, cursor, arguments, dialog)

        drop_table(connection, cursor, "temp")

        sql = """ALTER TABLE %(catchment_table)s
               ADD COLUMN the_nearest_node integer;

              CREATE TABLE IF NOT EXISTS temp AS
               SELECT a.gid, b.id, min(a.dist)

               FROM
                 (SELECT %(catchment_table)s.%(catchment_id)s as gid,
                         min(st_distance(
                         %(catchment_table)s.%(catchment_geom)s,
                         nodes.the_geom))
                          AS dist
                  FROM %(catchment_table)s, nodes
                  GROUP BY %(catchment_table)s.%(catchment_id)s) AS a,
                 (SELECT %(catchment_table)s.%(catchment_id)s as gid,
                 nodes.id, st_distance(
                 %(catchment_table)s.%(catchment_geom)s,
                 nodes.the_geom) AS dist
                  FROM %(catchment_table)s, nodes) AS b
               WHERE a.dist = b. dist
                     AND a.gid = b.gid
               GROUP BY a.gid, b.id; """ % arguments
        sql = clean_query(sql)

        cursor.execute(sql)
        connection.commit()

        populate_catchment_table(connection, cursor, arguments, dialog)

    except Exception as exception:
        message = "Error in updating catchment table \n {}". \
            format(str(exception))

        display_warning_message_box(
            dialog, "Error",
            message
        )

        raise IsochroneDBError


def update_catchment_table(connection, cursor, arguments, dialog):
    """Remove if nearest nodes column exists so we can updated the values.

    :param connection: Database connection
    :type connection:

    :param cursor: Database connection cursor
    :type cursor:

    :param arguments: List of required parameters in
     querying the database
    :type arguments: {}

    :param dialog: Dialog attached to this method
    :type dialog: Qdialog

    """
    sql = """ALTER TABLE %(catchment_table)s
           DROP COLUMN IF EXISTS the_nearest_node;""" % arguments

    sql = clean_query(sql)

    cursor.execute(sql)
    connection.commit()


def drop_network_cache(connection, cursor, arguments, dialog):
    """Clear a network cache if exists
    :param connection: Database connection
    :type connection:
    :param cursor: Database connection cursor
    :type cursor:
    :param arguments: List of required parameters in
     querying the database
    :type arguments: {}
    :param dialog: Dialog attached to this method
    :type dialog: Qdialog
    """

    try:
        sql = """DROP VIEW IF EXISTS network_cache"""

        sql = clean_query(sql)

        cursor.execute(sql)
        connection.commit()

    except Exception as exception:
        message = "Error in clearing network view \n {}". \
            format(str(exception))

        display_warning_message_box(
            dialog, "Error",
            message
        )

        raise IsochroneDBError


def drop_table(connection, cursor, table):
    """Drops temp table.

    :param connection: Database connection
    :type connection:

    :param cursor: Database connection cursor
    :type cursor:

    :param table: Table to be dropped
    :type table: str

    :param arguments: List of required parameters in
     querying the database
    :type arguments: {}

    :param dialog: Dialog attached to this method
    :type dialog: Qdialog

    """
    sql = """ DROP TABLE IF EXISTS {} """.format(table)
    sql = clean_query(sql)

    cursor.execute(sql)

    connection.commit()


def populate_catchment_table(connection, cursor, arguments, dialog):
    """Assign the nearest nodes to catchment respective column

    :param connection: Database connection
    :type connection:

    :param cursor: Database connection cursor
    :type cursor:

    :param arguments: List of required parameters in
     querying the database
    :type arguments: {}

    :param dialog: Dialog attached to this method
    :type dialog: Qdialog

    """

    sql = """UPDATE %(catchment_table)s
        SET the_nearest_node =
        (SELECT id
        FROM temp
        WHERE temp.gid =
         %(catchment_table)s.%(catchment_id)s LIMIT 1);""" % arguments

    sql = clean_query(sql)

    cursor.execute(sql)
    connection.commit()


def calculate_drivetimes(
        connection,
        cursor,
        arguments,
        progress_dialog,
        dialog,
        progress_percentage):

    """
    :param connection: Database connection
    :type connection:

    :param cursor: Database connection cursor
    :type cursor:

    :param arguments: List of required parameters in
     querying the database
    :type arguments: {}

    :param progress_dialog: Progress Dialog
    :type progress_dialog: Qdialog

    :param dialog: Dialog attached to this method
    :type dialog: Qdialog

    :param progress_percentage: the percentage of progress bar
    :type progress_percentage: int

    :returns Progress percentage
    :rtype int

    """

    index = 0

    try:
        rows = query_nearest_nodes(connection, cursor, arguments, dialog)

        # Convert unique column to integer as required by
        # the pgr_dijkstra function

        sql = """ALTER TABLE routable_network ALTER COLUMN
                %(network_id)s SET DATA TYPE int4""" % arguments

        sql = clean_query(sql)

        cursor.execute(sql)
        connection.commit()

        drop_table(connection, cursor, "catchment_with_cost")

        for row in rows:
            # This step is 45% of all steps so calculating
            # percentage of each increment accordingly

            percentage = 45 / len(rows)
            percentage = round(percentage, 0)
            catchment_id = row[0]


            arguments["catchment_current_id"] = catchment_id[0] \
                if isinstance(catchment_id, tuple) else catchment_id
            arguments["last_row_id"] = rows[len(rows) - 1][0] \
                if isinstance(rows[len(rows) - 1], tuple) else rows[len(rows) - 1]

            if index == 0:
                sql = """ CREATE TABLE
                        IF NOT EXISTS catchment_with_cost AS
                    SELECT
                    id,
                    the_geom,
                    (SELECT sum(cost) FROM (
                       SELECT * FROM pgr_dijkstra('
                       SELECT %(network_id)s AS id,
                          start_id::int4 AS source,
                          end_id::int4 AS target,
                          cost::float8 AS cost
                       FROM routable_network',
                       %(catchment_current_id)s,
                       id,
                       false)) AS foo ) AS cost
                    FROM nodes;""" % arguments
                sql = clean_query(sql)
                cursor.execute(sql)
            else:
                sql = """ INSERT INTO catchment_with_cost (
                    SELECT
                        id,
                        the_geom,
                        (SELECT sum(cost) FROM (
                           SELECT * FROM pgr_dijkstra('
                           SELECT  %(network_id)s AS id,
                              start_id::int4 AS source,
                              end_id::int4 AS target,
                              cost::float8 AS cost
                           FROM routable_network',
                           %(catchment_current_id)s,
                           id,
                           false)) AS foo ) AS cost
                    FROM nodes);""" % arguments

                sql = clean_query(sql)

                cursor.execute(sql)

            index += 1
            connection.commit()
            progress_percentage += percentage
            if progress_dialog:
                progress_dialog.setValue(int(progress_percentage))
                label_text = tr(
                    str(index) +
                    " catchment area(s) out of " +
                    str(len(rows)) +
                    " is(are) done")
                progress_dialog.setLabelText(label_text)

                if progress_dialog.wasCanceled():
                    return
        # if dialog:
        #     label_text = tr("Preparing all the catchment areas table")
        #     dialog.setLabelText(label_text)

    except Exception as exception:
        message = "Error in calculating drivetimes \n {}". \
            format(str(exception))

        display_warning_message_box(
            dialog, "Error",
            message
        )

        raise IsochroneDBError

    return progress_percentage


def query_nearest_nodes(connection, cursor, arguments, dialog):
    """

    :param connection: Database connection
    :type connection:

    :param cursor: Database connection cursor
    :type cursor:

    :param arguments: List of required parameters in
     querying the database
    :type arguments: {}

    :param dialog: Dialog attached to this method
    :type dialog: Qdialog

    """

    sql = """SELECT the_nearest_node from
        %(catchment_table)s""" % arguments

    sql = clean_query(sql)

    cursor.execute(sql)
    rows = cursor.fetchall()

    return rows


def prepare_drivetimes_table(connection, cursor, arguments, dialog):
    """

    :param connection: Database connection
    :type connection:

    :param cursor: Database connection cursor
    :type cursor:

    :param arguments: List of required parameters in
     querying the database
    :type arguments: {}

    :param dialog: Dialog attached to this method
    :type dialog: Qdialog

    :param progress_percentage: the percentage of progress bar
    :type progress_percentage: int

    """
    try:
        drop_table(connection, cursor, "catchment_final")

        sql = """ CREATE TABLE IF NOT EXISTS catchment_final AS
               SELECT id, the_geom, min (cost) AS %s
               FROM catchment_with_cost
               GROUP By id, the_geom
            """ % "drivetime"

        sql = clean_query(sql)
        cursor.execute(sql)
        connection.commit()

        # drop_table(connection, cursor, "catchment_final_mid")

        # TODO find best approach of getting max_hours
        # use these hours incase catchment is unreachable
        # maximum_time = max_drivetime(
        #     connection,
        #     cursor)
        #
        # max_hours = maximum_time + maximum_time * 0.05
        #
        # sql = """ CREATE TABLE catchment_final_mid AS
        #                 SELECT *, coalesce(drivetime, %f) as valid_drivetime
        #                 FROM catchment_final
        #                 """ % max_hours
        # sql = clean_query(sql)
        # cursor.execute(sql)
        # connection.commit()

        drop_table(connection, cursor, "catchment_final_no_null")

        sql = """ CREATE TABLE catchment_final_no_null AS
                SELECT *, (drivetime * 60) AS minutes FROM catchment_final
                WHERE %s IS NOT NULL
                """ % "drivetime"

        sql = clean_query(sql)
        cursor.execute(sql)
        connection.commit()

    except Exception as exception:
        message = "Error in preparing drivetimes table \n {}". \
            format(str(exception))

        display_warning_message_box(
            dialog,
            "Error",
            message
        )

        raise IsochroneDBError


def max_drivetime(connection, cursor):
    """ Return maximum drivetime

    :param connection: Database connection
    :type connection:

    :param cursor: Database connection cursor
    :type cursor:

    """

    sql = """SELECT coalesce(max(drivetime), 0) from
        catchment_final """

    sql = clean_query(sql)

    cursor.execute(sql)
    rows = cursor.fetchone()

    return rows[0]


def clean_query(query):
    """ Clean query for execution

    :param query: sql query
    :type query: str

    :return: cleaned sql query
    :rtype: str"""

    query = query.replace('\n', ' ')
    query = re.sub(r'\s+', ' ', query)
    query = query.replace('( ', '(')
    query = query.replace(' )', ')')
    query = query.strip()

    return query

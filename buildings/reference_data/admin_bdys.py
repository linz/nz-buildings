from builtins import str

# script to update canal data

from buildings.sql import buildings_reference_select_statements as reference_select
from buildings.utilities import database as db
from qgis.core import QgsVectorLayer

# TODO: review if the filter works
LAYERS = {
    "suburb_locality": {
        "layer_id": 113764,
        "primary_id": "id",
        "url_base": "https://data.linz.govt.nz",
        "cql_filter": "&cql_filter=type = 'Conservation Land' OR type = 'Island' OR type = 'Locality' OR type ='Suburb'",
    },
    "territorial_authority": {
        "layer_id": 39939,
        "primary_id": "TA_Code",
        "url_base": "https://datafinder.stats.govt.nz",
        "cql_filter": "",
    },
}

URI = "{1}/services;key={0}/wfs/layer-{2}-changeset?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&typeNames=layer-{2}-changeset&viewparams=from:{3};to:{4}{5}&SRSNAME=EPSG:2193&outputFormat=json"


def last_update(column_name):

    # get last update of layer date from log
    from_var = db.execute_return(
        reference_select.log_select_last_update.format(column_name)
    )
    from_var = from_var.fetchone()
    if from_var is None:
        # default to beginning of 2018
        from_var = (
            "2018-01-01T02:15:47.317439"  #  TODO: check if we should use another date
        )
    else:
        from_var = str(from_var[0]).split("+")[0]
        from_var = from_var.split(" ")
        from_var = from_var[0] + "T" + from_var[1]
    return from_var


def current_date():
    to_var = db.execute_return("SELECT now();")
    to_var = to_var.fetchone()[0]
    to_var = str(to_var).split("+")[0]
    to_var = to_var.split(" ")
    to_var = to_var[0] + "T" + to_var[1]
    return to_var


# todo: add kx_api_key in config
# todo: combine suburb_locality- and town city
def update_admin_bdys(kx_api_key, dataset, dbconn):

    # get last update of layer date from log
    from_var = last_update(dataset)

    # current date
    to_var = current_date()

    layer = QgsVectorLayer(
        URI.format(
            kx_api_key,
            LAYERS[dataset]["url_base"],
            LAYERS[dataset]["layer_id"],
            from_var,
            to_var,
            LAYERS[dataset]["cql_filter"],
        )
    )

    if not layer.isValid():
        # something went wrong
        return "error"

    if layer.featureCount() == 0:
        return "current"

    external_id = LAYERS[dataset]["primary_id"]

    ids_updates = []
    ids_attr_updates = []

    for feature in layer.getFeatures():
        if feature.attribute("__change__") == "DELETE":
            sql = "SELECT buildings_reference.{}_delete_by_external_id(%s)".format(
                dataset
            )
            result = dbconn.execute_no_commit(sql, (feature[external_id],))
            result = result.fetchone()
            if result is not None:
                ids_updates.append(result[0])

        elif feature.attribute("__change__") == "UPDATE":
            if dataset == "suburb_locality":
                result = dbconn.execute_return(
                    reference_select.suburb_locality_attribute_updates,
                    (
                        feature[external_id],
                        correct_name_format(feature["name"]),
                        correct_name_format(feature["major_name"]),
                    ),
                )
                result = result.fetchone()
                if result is not None:
                    ids_attr_updates.append(result[0])
                sql = "SELECT buildings_reference.suburb_locality_update_by_external_id(%s, %s, %s, %s)"
                result = dbconn.execute_no_commit(
                    sql,
                    (
                        feature[external_id],
                        correct_name_format(feature["name"]),
                        correct_name_format(feature["major_name"]),
                        feature.geometry().asWkt(),
                    ),
                )
                result = result.fetchone()
                if result is not None:
                    ids_updates.append(result[0])
            else:
                result = dbconn.execute_return(
                    reference_select.territorial_authority_attribute_updates,
                    (
                        feature[external_id],
                        correct_name_format(feature["name"]),
                    ),
                )
                result = result.fetchone()
                if result is not None:
                    ids_attr_updates.append(result[0])
                sql = "SELECT buildings_reference.territorial_authority_update_by_external_id(%s, %s, %s)"
                result = dbconn.execute_no_commit(
                    sql,
                    (
                        feature[external_id],
                        correct_name_format(feature["name"]),
                        feature.geometry().asWkt(),
                    ),
                )
                result = result.fetchone()
                if result is not None:
                    ids_updates.append(result[0])

        elif feature.attribute("__change__") == "INSERT":
            # Check if feature is already in reference table
            result = dbconn.execute_return(
                reference_select.select_admin_bdy_id_by_external_id.format(dataset),
                (feature[external_id],),
            )
            result = result.fetchone()
            if result is None:
                if dataset == "suburb_locality":
                    sql = "SELECT buildings_reference.suburb_locality_insert(%s, %s, %s, %s)"
                    dbconn.execute_no_commit(
                        sql,
                        (
                            feature[external_id],
                            correct_name_format(feature["name"]),
                            correct_name_format(feature["major_name"]),
                            feature.geometry().asWkt(),
                        ),
                    )
                else:
                    sql = "SELECT buildings_reference.territorial_authority_insert(%s, %s, %s)"
                    dbconn.execute_no_commit(
                        sql,
                        (
                            feature[external_id],
                            correct_name_format(feature["name"]),
                            feature.geometry().asWkt(),
                        ),
                    )
    print("updated_id {}".format(ids_updates))
    print("updated_attrs {}".format(ids_attr_updates))
    sql = "SELECT buildings_reference.{}_update_building_outlines(%s, %s)".format(
        dataset
    )
    dbconn.execute_no_commit(sql, (ids_updates, ids_attr_updates))

    return "updated"


def correct_name_format(name):
    if name:
        if "'" in name:
            name = "{}".format(name.replace("'", "''"))
    else:
        name = ""
    return str(name)

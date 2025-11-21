from builtins import str
from collections import Counter


# script to update canal data

from buildings.sql import buildings_reference_select_statements as reference_select
from buildings.utilities import database as db
from qgis.core import QgsVectorLayer
from qgis.PyQt.QtCore import Qt, QVariant

LDS_LAYER_IDS = {
    "nz_imagery_survey_index": 95677,
    "nz_facilities": 105588,
}


URI = "https://data.linz.govt.nz/services;key={1}/wfs/layer-{0}-changeset?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&typeNames=layer-{0}-changeset&viewparams=from:{2};to:{3}{4}&SRSNAME=EPSG:2193&outputFormat=json"


def last_update(column_name):

    # get last update of layer date from log
    from_var = db.execute_return(
        reference_select.log_select_last_update.format(column_name)
    )
    from_var = from_var.fetchone()
    if from_var is None:
        # default to beginning of 2018
        from_var = "2018-01-01T02:15:47.317439"
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


def check_status_other_reference(kx_api_key, dataset):
    # get last update of layer date from log
    if dataset == "nz_imagery_survey_index":
        from_var = last_update("imagery_survey_index")
    elif dataset == "nz_facilities":
        from_var = last_update("facilities")

    # current date
    to_var = current_date()

    cql_filter = ""
    layer = QgsVectorLayer(
        URI.format(LDS_LAYER_IDS[dataset], kx_api_key, from_var, to_var, cql_filter)
    )
    if not layer.isValid():
        return {
            "dataset": dataset,
            "last_updated": from_var,
            "new_updates": "error",
            "insert": "error",
            "update": "error",
            "delete": "error",
        }

    if layer.featureCount() == 0:
        return {
            "dataset": dataset,
            "last_updated": from_var,
            "new_updates": "",
            "insert": "0",
            "update": "0",
            "delete": "0",
        }
    counts = Counter([feat["__change__"] for feat in layer.getFeatures()])
    return {
        "dataset": dataset,
        "last_updated": from_var,
        "new_updates": "Available",
        "insert": str(counts["INSERT"]),
        "update": str(counts["UPDATE"]),
        "delete": str(counts["DELETE"]),
    }


def update_imagery_survey_index(kx_api_key, dataset, dbconn):
    if dataset != "nz_imagery_survey_index":
        return "error"

    # get last update of layer date from log
    from_var = last_update("imagery_survey_index")

    # current date
    to_var = current_date()

    cql_filter = ""
    external_id = "imagery_survey_id"

    layer = QgsVectorLayer(
        URI.format(LDS_LAYER_IDS[dataset], kx_api_key, from_var, to_var, cql_filter)
    )
    if not layer.isValid():
        # something went wrong
        return "error"

    if layer.featureCount() == 0:
        return "current"

    for feature in layer.getFeatures():
        if feature.attribute("__change__") == "DELETE":
            sql = "DELETE FROM buildings_reference.nz_imagery_survey_index WHERE imagery_survey_id = %s;"
            dbconn.execute_no_commit(sql, (feature[external_id],))

        elif feature.attribute("__change__") == "INSERT":
            sql = "SELECT True FROM buildings_reference.nz_imagery_survey_index WHERE imagery_survey_id = %s;"
            result = dbconn.execute_return(
                sql,
                (feature[external_id],),
            )
            result = result.fetchone()
            if result is None:
                sql = """  
                    INSERT INTO buildings_reference.nz_imagery_survey_index (
                        imagery_survey_id,
                        name,
                        imagery_id,
                        index_id,
                        set_order,
                        ground_sample_distance,
                        accuracy,
                        supplier,
                        licensor,
                        flown_from,
                        flown_to,
                        shape)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_GeometryFromText(%s), 2193))
                    """
                dbconn.execute_no_commit(
                    sql,
                    (
                        feature[external_id],
                        correct_attribute_format(feature["name"]),
                        correct_attribute_format(feature["imagery_id"]),
                        correct_attribute_format(feature["index_id"]),
                        correct_attribute_format(feature["set_order"]),
                        correct_attribute_format(feature["ground_sample_distance"]),
                        correct_attribute_format(feature["accuracy"]),
                        correct_attribute_format(feature["supplier"]),
                        correct_attribute_format(feature["licensor"]),
                        feature["flown_from"].toString(Qt.ISODate),
                        feature["flown_to"].toString(Qt.ISODate),
                        feature.geometry().asWkt(),
                    ),
                )

        elif feature.attribute("__change__") == "UPDATE":
            sql = """  
                UPDATE buildings_reference.nz_imagery_survey_index
                SET
                    name = %s,
                    imagery_id = %s,
                    index_id = %s,
                    set_order = %s,
                    ground_sample_distance = %s,
                    accuracy = %s,
                    supplier = %s,
                    licensor = %s,
                    flown_from = %s,
                    flown_to = %s,
                    shape = ST_SetSRID(ST_GeometryFromText(%s), 2193)
                WHERE imagery_survey_id = %s;
                """
            dbconn.execute_no_commit(
                sql,
                (
                    correct_attribute_format(feature["name"]),
                    correct_attribute_format(feature["imagery_id"]),
                    correct_attribute_format(feature["index_id"]),
                    correct_attribute_format(feature["set_order"]),
                    correct_attribute_format(feature["ground_sample_distance"]),
                    correct_attribute_format(feature["accuracy"]),
                    correct_attribute_format(feature["supplier"]),
                    correct_attribute_format(feature["licensor"]),
                    feature["flown_from"].toString(Qt.ISODate),
                    feature["flown_to"].toString(Qt.ISODate),
                    feature.geometry().asWkt(),
                    feature[external_id],
                ),
            )
    return "updated"


def update_facilities(kx_api_key, dataset, dbconn):
    if dataset != "nz_facilities":
        return "error"

    # get last update of layer date from log
    from_var = last_update("facilities")

    # current date
    to_var = current_date()

    cql_filter = ""
    external_id = "facility_id"

    layer = QgsVectorLayer(
        URI.format(LDS_LAYER_IDS[dataset], kx_api_key, from_var, to_var, cql_filter)
    )
    if not layer.isValid():
        # something went wrong
        return "error"

    if layer.featureCount() == 0:
        return "current"

    for feature in layer.getFeatures():
        if feature.attribute("__change__") == "DELETE":
            sql = "DELETE FROM buildings_reference.nz_facilities WHERE facility_id = %s;"
            dbconn.execute_no_commit(sql, (feature[external_id],))

        elif feature.attribute("__change__") == "INSERT":
            sql = "SELECT True FROM buildings_reference.nz_facilities WHERE facility_id = %s;"
            result = dbconn.execute_return(
                sql,
                (feature[external_id],),
            )
            result = result.fetchone()
            if result is None:
                sql = """  
                    INSERT INTO buildings_reference.nz_facilities (
                        facility_id,
                        source_facility_id,
                        name,
                        source_name,
                        use,
                        use_type,
                        use_subtype,
                        estimated_occupancy,
                        last_modified,
                        shape)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_GeometryFromText(%s), 2193))
                    """
                dbconn.execute_no_commit(
                    sql,
                    (
                        feature[external_id],
                        correct_attribute_format(feature["source_facility_id"]),
                        correct_attribute_format(feature["name"]),
                        correct_attribute_format(feature["source_name"]),
                        correct_attribute_format(feature["use"]),
                        correct_attribute_format(feature["use_type"]),
                        correct_attribute_format(feature["use_subtype"]),
                        correct_attribute_format(feature["estimated_occupancy"]),
                        feature["last_modified"].toString(Qt.ISODate),
                        feature.geometry().asWkt(),
                    ),
                )

        elif feature.attribute("__change__") == "UPDATE":
            sql = """  
                UPDATE buildings_reference.nz_facilities
                SET
                    source_facility_id = %s,
                    name = %s,
                    source_name = %s,
                    use = %s,
                    use_type = %s,
                    use_subtype = %s,
                    estimated_occupancy = %s,
                    last_modified = %s,
                    shape = ST_SetSRID(ST_GeometryFromText(%s), 2193)
                WHERE facility_id = %s;
                """
            dbconn.execute_no_commit(
                sql,
                (
                    correct_attribute_format(feature["source_facility_id"]),
                    correct_attribute_format(feature["name"]),
                    correct_attribute_format(feature["source_name"]),
                    correct_attribute_format(feature["use"]),
                    correct_attribute_format(feature["use_type"]),
                    correct_attribute_format(feature["use_subtype"]),
                    correct_attribute_format(feature["estimated_occupancy"]),
                    feature["last_modified"].toString(Qt.ISODate),
                    feature.geometry().asWkt(),
                    feature[external_id],
                ),
            )
    return "updated"


def correct_attribute_format(value):
    if type(value) == QVariant and value.isNull():
        return None
    return value

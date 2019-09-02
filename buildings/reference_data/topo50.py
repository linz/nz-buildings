# script to update canal data

from buildings.sql import buildings_reference_select_statements as reference_select
from buildings.utilities import database as db
from qgis.core import QgsVectorLayer

LDS_LAYER_IDS = {
    'canal_polygons': 50251,
    'lagoon_polygons': 50292,
    'lake_polygons': 50293,
    'pond_polygons': 50310,
    'river_polygons': 50328,
    'swamp_polygons': 50359,
    'hut_points': 50245,
    'shelter_points': 50245,
    'bivouac_points': 50239,
    'protected_areas_polygons': 53564,
}

URI = 'srsname=\'EPSG:2193\' typename=\'data.linz.govt.nz:layer-{0}-changeset\' url="https://data.linz.govt.nz/services;key={1}/wfs/layer-{0}-changeset?viewparams=from:{2};to:{3}{4}"'


def last_update(column_name):

    # get last update of layer date from log
    from_var = db.execute_return(reference_select.log_select_last_update.format(column_name))
    from_var = from_var.fetchone()
    if from_var is None:
        # default to beginning of 2018
        from_var = '2018-01-01T02:15:47.317439'
    else:
        from_var = str(from_var[0]).split('+')[0]
        from_var = from_var.split(' ')
        from_var = from_var[0] + 'T' + from_var[1]
    return from_var


def current_date():
    to_var = db.execute_return('SELECT now();')
    to_var = to_var.fetchone()[0]
    to_var = str(to_var).split('+')[0]
    to_var = to_var.split(' ')
    to_var = to_var[0] + 'T' + to_var[1]
    return to_var


def update_topo50(kx_api_key, dataset):

    # Get name of column in reference log table
    if 'polygon' in dataset:
        column_name = dataset.replace('_polygons', '')
    elif 'point' in dataset:
        column_name = dataset.replace('_points', '')
    else:
        column_name = dataset

    # get last update of layer date from log
    from_var = last_update(column_name)

    # current date
    to_var = current_date()

    cql_filter = ''
    if dataset == 'hut_points':
        cql_filter = '&cql_filter=bldg_use=\'hut\''
    elif dataset == 'shelter_points':
        cql_filter = '&cql_filter=bldg_use=\'shelter\''
    elif dataset == 'protected_areas_polygons':
        cql_filter = '&cql_filter=type = \'Conservation Area\' OR type = \'National Park\' OR type =\'Wildlife Area\''

    external_id = 't50_fid'
    if dataset == 'protected_areas_polygons':
        external_id = 'napalis_id'

    layer = QgsVectorLayer(URI.format(LDS_LAYER_IDS[dataset], kx_api_key, from_var, to_var, cql_filter), "changeset", "WFS")

    if not layer.isValid():
        # something went wrong
        return 'error'

    if layer.featureCount() == 0:
        return 'current'

    for feature in layer.getFeatures():
        if feature.attribute('__change__') == 'DELETE':
            sql = 'SELECT buildings_reference.{}_delete_by_external_id(%s)'.format(dataset)
            db.execute(sql, (feature.attribute(external_id),))

        elif feature.attribute('__change__') == 'INSERT':
            if 'polygon' in dataset:
                result = db.execute_return(
                    reference_select.select_polygon_id_by_external_id.format(column_name), (feature.attribute(external_id),))
            elif 'point' in dataset:
                result = db.execute_return(reference_select.select_point_id_by_external_id.format(column_name), (feature.attribute(external_id),))
            result = result.fetchone()
            if result is None:
                sql = 'SELECT buildings_reference.{}_insert(%s, %s, %s)'.format(dataset)
                db.execute(sql, (feature.attribute(external_id), correct_name_format(feature['name']), feature.geometry().exportToWkt()))

        elif feature.attribute('__change__') == 'UPDATE':
            sql = 'SELECT buildings_reference.{}_update_by_external_id(%s, %s, %s)'.format(dataset)
            db.execute(sql, (feature.attribute(external_id), correct_name_format(feature['name']), feature.geometry().exportToWkt()))
    return 'updated'


def correct_name_format(name):
    if name:
        if "'" in name:
            name = "{}".format(name.replace("'", "''"))
    else:
        name = ''
    return str(name)

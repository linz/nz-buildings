# script to update canal data

from buildings.sql import buildings_reference_select_statements as reference_select
from buildings.utilities import database as db
from qgis.core import QgsVectorLayer

LDS_LAYER_IDS = {
      'canal_polygons': 50251
    , 'lagoon_polygons': 50292
    , 'lake_polygons': 50293
    , 'pond_polygons': 50310
    , 'river_polygons': 50328
    , 'swamp_polygons': 50359
    , 'hut_points': 50245
    , 'shelter_points': 50245
    , 'bivouac_points': 50239
    , 'protected_areas': 53564
}

URI = 'srsname=\'EPSG:2193\' typename=\'data.linz.govt.nz:layer-{0}-changeset\' url="https://data.linz.govt.nz/services;key={1}/wfs/layer-{0}-changeset?viewparams=from:{2};to:{3}{4}"'


def last_update(dataset):
    # get last update of layer date from log
    from_var = db.execute_return(reference_select.log_select_last_update.format(dataset))
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

    # get last update of layer date from log
    from_var = last_update(dataset)

    # current date
    to_var = current_date()

    cql_filter = ''
    if dataset == 'hut_points':
        cql_filter = '&cql_filter=bldg_use=\'hut\''
    elif dataset == 'shelter_points':
        cql_filter = '&cql_filter=bldg_use=\'shelter\''

    layer = QgsVectorLayer(URI.format(LDS_LAYER_IDS[dataset], kx_api_key, from_var, to_var, cql_filter), "changeset", "WFS")

    if not layer.isValid():
        # something went wrong
        return 'error'

    if layer.featureCount() == 0:
        return 'current'

    for feature in layer.getFeatures():
        if feature.attribute('__change__') == 'DELETE':
            sql = 'SELECT buildings_reference.{}_delete_by_external_id(%s)'.format(dataset)
            db.execute(sql, (feature.attribute('t50_fid'),))

        elif feature.attribute('__change__') == 'INSERT':
            result = db.execute_return(reference_select.select_polygon_id_by_external_id.format(dataset), (feature.attribute('t50_fid'),))
            result = result.fetchone()
            if result is None:
                sql = 'SELECT buildings_reference.{}_insert(%s, %s)'.format(dataset)
                db.execute(sql, (feature.attribute('t50_fid'), feature.geometry().exportToWkt()))

        elif feature.attribute('__change__') == 'UPDATE':
            sql = 'SELECT buildings_reference.{}_update_shape_by_external_id(%s, %s)'.format(dataset)
            db.execute(sql, (feature.attribute('t50_fid'), feature.geometry().exportToWkt()))
    return 'updated'

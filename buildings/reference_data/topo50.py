# script to update canal data

from buildings.sql import buildings_reference_select_statements as reference_select
from buildings.utilities import database as db
from qgis.core import QgsVectorLayer

LDS_LAYER_IDS = {'canal': 50251, 'lagoon': 50292, 'lake': 50293, 'pond': 50310, 'river': 50328, 'swamp': 50359}
URI = 'srsname=\'EPSG:2193\' typename=\'data.linz.govt.nz:layer-{0}-changeset\' url=\'https://data.linz.govt.nz/services;key={1}/wfs/layer-{0}-changeset?viewparams=from:{2};to:{3}\' version=\'auto\' table="" sql='


def last_update(dataset):
    # get last update of layer date from log
    from_var = db._execute(reference_select.log_select_last_update.format(dataset))
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
    to_var = db._execute('SELECT now();')
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

    layer = QgsVectorLayer(URI.format(LDS_LAYER_IDS[dataset], kx_api_key, from_var, to_var), "canal_changeset", "WFS")

    if not layer.isValid():
        # something went wrong
        return 'error'

    if layer.featureCount() == 0:
        return 'current'

    for feature in layer.getFeatures():
        if feature.attribute('__change__') == 'DELETE':
            sql = 'SELECT buildings_reference.{}_polygons_delete_by_external_id(%s)'.format(dataset)
            db.execute(sql, (feature.attribute('t50_fid'),))

        elif feature.attribute('__change__') == 'INSERT':
            result = db._execute(reference_select.select_polygon_id_by_external_id.format(dataset), (feature.attribute('t50_fid'),))
            result = result.fetchone()
            if result is None:
                sql = 'SELECT buildings_reference.{}_polygons_insert(%s, %s)'.format(dataset)
                db.execute(sql, (feature.attribute('t50_fid'), feature.geometry().exportToWkt()))

        elif feature.attribute('__change__') == 'UPDATE':
            sql = 'SELECT buildings_reference.{}_polygons_update_shape_by_external_id(%s, %s)'.format(dataset)
            db.execute(sql, (feature.attribute('t50_fid'), feature.geometry().exportToWkt()))
    return 'updated'

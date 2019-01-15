# script to update pond data

from buildings.sql import buildings_reference_select_statements as reference_select
from buildings.utilities import database as db
from qgis.core import QgsVectorLayer


def update_ponds(kx_api_key):

    # get last update of layer date from log
    from_var = db._execute(reference_select.update_log_pond_date)
    from_var = from_var.fetchone()
    if from_var is None:
        # default to beginning of 2018
        from_var = '2018-01-01T02:15:47.317439'
    else:
        from_var = str(from_var[0]).split('+')[0]
        from_var = from_var.split(' ')
        from_var = from_var[0] + 'T' + from_var[1] + ''

    # current date
    to_var = db._execute('SELECT now();')
    to_var = to_var.fetchone()[0]
    to_var = str(to_var).split('+')[0]
    to_var = to_var.split(' ')
    to_var = to_var[0] + 'T' + to_var[1]

    uri = 'srsname=\'EPSG:2193\' typename=\'data.linz.govt.nz:layer-50310-changeset\' url=\'https://data.linz.govt.nz/services;key={0}/wfs/layer-50310-changeset?viewparams=from:{1};to:{2}\' version=\'auto\' table="" sql='.format(
        kx_api_key, from_var, to_var)
    layer = QgsVectorLayer(uri, "pond_changeset", "WFS")

    if not layer.isValid():
        # something went wrong
        return 'error'

    if layer.featureCount() == 0:
        return 'current'

    for feature in layer.getFeatures():
        if feature.attribute('__change__') == 'DELETE':
            sql = 'SELECT buildings_reference.pond_polygons_delete_by_external_id(%s)'
            db.execute(sql, (feature.attribute('t50_fid'),))

        elif feature.attribute('__change__') == 'INSERT':
            result = db._execute(reference_select.pond_polygon_id_by_external_id, (feature.attribute('t50_fid'),))
            result = result.fetchone()
            if result is None:
                sql = 'SELECT buildings_reference.pond_polygons_insert(%s, %s)'
                db.execute(sql, (feature.attribute('t50_fid'), feature.geometry().exportToWkt()))

        elif feature.attribute('__change__') == 'UPDATE':
            sql = 'SELECT buildings_reference.pond_polygons_update_shape_by_external_id(%s, %s)'
            db.execute(sql, (feature.attribute('t50_fid'), feature.geometry().exportToWkt()))
    return 'updated'

import processing
from PyQt4.QtCore import *

# Adding Building id Field for Existing Potential Matches
provider = PM_existing.dataProvider()

Build_id = [feat.id() for feat in PM_existing.getFeatures()]

field = QgsField("Build_id", QVariant.Double)
provider.addAttributes([field])
PM_existing.updateFields()

idx = PM_existing.fieldNameIndex('Build_id')

for bid in BuildID:
    new_values = {idx: bid}
    provider.changeAttributeValues({Build_id.index(bid): new_values})

    #################################################################
# Adding empty Building id field for Incoming Potential Matches
providerI = PM_incoming.dataProvider()

fieldI = QgsField("Build_id", QVariant.Double)
providerI.addAttributes([fieldI])
PM_incoming.updateFields()

idxI = PM_incoming.fieldNameIndex('Build_id')

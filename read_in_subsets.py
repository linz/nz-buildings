from qgis.utils import iface
from PyQt4.QtGui import *

qid = QInputDialog()
title = "Enter Following Details"
label = "Existing Data file location and name: "
mode = QLineEdit.Normal
default = "<enter here>"

input_existing_text, ok = QInputDialog.getText(qid, title, label, mode, default)


title2 = "Enter Following Details"
label2 = "Incoming Data file location and name: "
mode2 = QLineEdit.Normal
default2 = "<enter here>"

input_incoming_text, ok = QInputDialog.getText(qid, title2, label2, mode2, default2)

existingLayer = iface.addVectorLayer(input_existing_text, "1-", "ogr")
if not existingLayer:
    print "existing layer not found"
incomingLayer = iface.addVectorLayer(input_incoming_text, "2-", "ogr")
if not incomingLayer:
    print "incoming layer not found"

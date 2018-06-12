#/***************************************************************************
# qgis-building-plugin
#
# qgis-buildings-plugin
#							 -------------------
#		begin				: 2018-03-26
#		git sha				: $Format:%H$
#		copyright			: (C) 2018 by LINZ
#		email				:
# ***************************************************************************/


PLUGINNAME = buildings

AF = buildings/gui/i18n/af.ts

deploy:
	@echo
	@echo "------------------------------------------"
	@echo "Deploying plugin to your .qgis2 directory."
	@echo "------------------------------------------"
	# The deploy target only works on unix like operating system where
	# the Python plugin directory is located at:
	# $HOME/$(QGISDIR)/python/plugins
	rm -rf $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -TRv $(PLUGINNAME) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)

setup_test_db:
	@echo
	@echo "------------------------------------------"
	@echo "Setting up schema in nz-buildings-plugin-db"
	@echo "------------------------------------------"
	export PGDATABASE=nz-buildings-plugin-db; \
	dropdb --if-exists $$PGDATABASE; \
	createdb $$PGDATABASE; \
	nz-buildings-load nz-buildings-plugin-db --with-plugin-setup; \
	sed -i '4s/.*/dbname=nz-buildings-plugin-db/' ~/.qgis2/$(PLUGINNAME)/pg_config.ini

test:
	@echo
	@echo "------------------------------------------"
	@echo "Running Unit Tests on Buildings Plugin"
	@echo "------------------------------------------"
	@echo
	python -c 'from buildings.tests import open_qgis; open_qgis.open_qgis()'

reset_db:
	@echo
	@echo "------------------------------------------"
	@echo "re-connecting plugin to linz_db"
	@echo "------------------------------------------"
	sed -i '4s/.*/dbname=linz_db/' ~/.qgis2/$(PLUGINNAME)/pg_config.ini

setup_db:
	@echo
	@echo "------------------------------------------"
	@echo "Setting up schema in linz_db"
	@echo "------------------------------------------"
	export PGDATABASE=linz_db; \
	nz-buildings-load linz_db; \

# The dclean target removes compiled python files from plugin directory
# also deletes any .git entry
dclean:
	@echo
	@echo "-----------------------------------"
	@echo "Removing any compiled python files."
	@echo "-----------------------------------"
	find $(HOME)/.qgis2/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/.qgis2/python/plugins/$(PLUGINNAME) -iname ".git" -prune -exec rm -Rf {} \;

derase:
	@echo
	@echo "-------------------------"
	@echo "Removing deployed plugin."
	@echo "-------------------------"
	rm -Rf $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)

zip: deploy dclean
	@echo
	@echo "---------------------------"
	@echo "Creating plugin zip bundle."
	@echo "---------------------------"
	# The zip target deploys the plugin and creates a zip file with the deployed
	# content.
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/.qgis2/python/plugins; zip -9r $(HOME)/.qgis2/python/plugins/$(PLUGINNAME).zip $(PLUGINNAME)

package:
	# Create a zip package of the plugin named $(PLUGINNAME).zip.
	# This requires use of git (your plugin development directory must be a
	# git repository).
	# To use, pass a valid commit or tag as follows:
	#   make package VERSION=Version_0.3.2
	@echo
	@echo "------------------------------------"
	@echo "Exporting plugin to zip package.	"
	@echo "------------------------------------"
	rm -f $(PLUGINNAME).zip
	git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
	echo "Created package: $(PLUGINNAME).zip"

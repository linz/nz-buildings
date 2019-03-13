# DB

# Installs the SQL creation scripts and load script.

VERSION = 1.2.0
REVISION = $(shell test -d .git && git describe --always || echo $(VERSION))

SED = sed

datadir = ${DESTDIR}/usr/share/nz-buildings
bindir = ${DESTDIR}/usr/bin

# List of SQL scripts used for installation
# Includes SQL scripts that are only built during install
SQLSCRIPTS = \
  db/sql/buildings_reference/01-create-schema-and-tables.sql \
  db/sql/buildings_common/01-create-schema-and-tables.sql \
  db/sql/buildings/01-create-schema-and-tables.sql \
  db/sql/buildings_bulk_load/01-create-schema-and-tables.sql \
  db/sql/buildings_lds/01-create-schema-and-tables.sql \
  db/sql/buildings_reference/02-default-values.sql \
  db/sql/buildings_common/02-default-values.sql \
  db/sql/buildings/02-default-values.sql \
  db/sql/buildings_bulk_load/02-default-values.sql \
  db/sql/buildings_lds/02-default-values.sql \
  db/sql/buildings_bulk_load/03-alter_relationships_create_view.sql \
  db/sql/01-buildings_version.sql \
  db/sql/buildings_reference/functions/01-canal_polygons.sql \
  db/sql/buildings_reference/functions/02-capture_source_area.sql \
  db/sql/buildings_reference/functions/03-lagoon_polygons.sql \
  db/sql/buildings_reference/functions/04-lake_polygons.sql \
  db/sql/buildings_reference/functions/05-pond_polygons.sql \
  db/sql/buildings_reference/functions/06-reference_update_log.sql \
  db/sql/buildings_reference/functions/07-river_polygons.sql \
  db/sql/buildings_reference/functions/08-suburb_locality.sql \
  db/sql/buildings_reference/functions/09-swamp_polygons.sql \
  db/sql/buildings_reference/functions/10-territorial_authority_and_territorial_authority_grid.sql \
  db/sql/buildings_reference/functions/11-town_city.sql \
  db/sql/buildings_common/functions/01-capture_method.sql \
  db/sql/buildings_common/functions/02-capture_source_group.sql \
  db/sql/buildings_common/functions/03-capture_source.sql \
  db/sql/buildings/functions/01-lifecycle_stage.sql \
  db/sql/buildings/functions/02-use.sql \
  db/sql/buildings/functions/03-buildings.sql \
  db/sql/buildings/functions/04-building_outlines.sql \
  db/sql/buildings/functions/05-building_name.sql \
  db/sql/buildings/functions/06-building_use.sql \
  db/sql/buildings/functions/07-lifecycle.sql \
  db/sql/buildings_bulk_load/functions/01-organisation.sql \
  db/sql/buildings_bulk_load/functions/02-bulk_load_status.sql \
  db/sql/buildings_bulk_load/functions/03-qa_status.sql \
  db/sql/buildings_bulk_load/functions/04-supplied_datasets.sql \
  db/sql/buildings_bulk_load/functions/05-bulk_load_outlines.sql \
  db/sql/buildings_bulk_load/functions/06-existing_subset_extracts.sql \
  db/sql/buildings_bulk_load/functions/07-added.sql \
  db/sql/buildings_bulk_load/functions/08-removed.sql \
  db/sql/buildings_bulk_load/functions/09-related.sql \
  db/sql/buildings_bulk_load/functions/10-matched.sql \
  db/sql/buildings_bulk_load/functions/11-transferred.sql \
  db/sql/buildings_bulk_load/functions/12-deletion_description.sql \
  db/sql/buildings_bulk_load/functions/13-supplied_outlines.sql \
  db/sql/buildings_bulk_load/functions/14-compare_buildings.sql \
  db/sql/buildings_lds/functions/01-nz_building_outlines.sql \
  db/sql/buildings_lds/functions/02-nz_building_outlines_full_history.sql \
  db/sql/buildings_lds/functions/03-nz_building_outlines_lifecycle.sql \
  db/sql/buildings_lds/functions/04-load_buildings.sql \
  db/sql/buildings_lds/functions/05-populate_buildings_lds.sql \
  $(END)

# List of scripts built during install
SCRIPTS_built = \
	db/scripts/nz-buildings-load \
	$(END)

# List of files built from .in files during install
EXTRA_CLEAN = \
	db/sql/01-buildings_version.sql \
	$(SCRIPTS_built)

.dummy:

# Need install to depend on something for debuild

all: $(SQLSCRIPTS) $(SCRIPTS_built)

# Iterate through .sql.in files and build a .sql version
# with @@VERSION@@ and @@REVISION@@ replaced
%.sql: %.sql.in makefile
	$(SED) -e 's/@@VERSION@@/$(VERSION)/;s|@@REVISION@@|$(REVISION)|' $< > $@

# Replace @@VERSION@@ and @@REVISION@@ in schema load script
db/scripts/nz-buildings-load: db/scripts/nz-buildings-load.in
	$(SED) -e 's/@@VERSION@@/$(VERSION)/;s|@@REVISION@@|$(REVISION)|' $< >$@
	chmod +x $@

# Copy scripts to local data directory
# Allow nz-buildings-load to be executed from anywhere
install: $(SQLSCRIPTS) $(SCRIPTS_built)
	mkdir -p ${datadir}/sql
	cp -R db/sql/* ${datadir}/sql
	mkdir -p ${datadir}/tests/testdata
	cp db/tests/testdata/*.sql ${datadir}/tests/testdata
	mkdir -p ${bindir}
	cp $(SCRIPTS_built) ${bindir}

uninstall:
	# Remove the SQL scripts installed locally
	rm -rf ${datadir}

check test: $(SQLSCRIPTS)
	# Build a test database and run unit tests
	export PGDATABASE=nz-buildings-pgtap-db; \
	dropdb --if-exists $$PGDATABASE; \
	createdb $$PGDATABASE; \
	nz-buildings-load nz-buildings-pgtap-db --with-test-data; \
	pg_prove db/tests/

clean:
	# Remove the files built from .in files during install
	rm -f $(EXTRA_CLEAN)

# PLUGIN

PLUGINNAME = buildings

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
	$(SED) -i '4s/.*/dbname=nz-buildings-plugin-db/' ~/.qgis2/$(PLUGINNAME)/pg_config.ini

update_ui_headers:
	@echo
	@echo "------------------------------------------"
	@echo "Fix/revert header lines in .ui files to qgis.gui"
	@echo "------------------------------------------"
	for f in ./buildings/gui/*.ui; do \
		$(SED) -i -e 's|<header>.*</header>|<header>qgis.gui</header>|g' $$f; \
	done;

bump_version:
	@echo
	@echo "------------------------------------------"
	@echo "Bump version"
	@echo "------------------------------------------"
	# Update version number in QGIS Plugin
	$(SED) -i 's/^version=.*/version=$(VERSION)/g' ./buildings/metadata.txt
	# Add today's date for latest release in CHANGELOG
	$(SED) -i '/Unreleased/{n;n;s/.*/$(TODAY)\n/}' ./CHANGELOG.rst
	# Replace Unreleased header with version number in CHANGELOG
	$(SED) -i 's/Unreleased/$(VERSION)/g' ./CHANGELOG.rst
	# Replace version number in makefile
	$(SED) -i 's/^VERSION = .*/VERSION = $(VERSION)/g' ./makefile

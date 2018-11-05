# Installs the SQL creation scripts and load script.
# TODO: Create a simple rebuild-buildings $DB_NAME alias that can be used to
# repeatedly reinstall and rebuild the nz-buildings database.

VERSION = dev
REVISION = $(shell test -d .git && git describe --always || echo $(VERSION))

SED = sed

datadir = ${DESTDIR}/usr/share/nz-building-outlines
bindir = ${DESTDIR}/usr/bin

# List of SQL scripts used for installation
# Includes SQL scripts that are only built during install
SQLSCRIPTS = \
  sql/buildings_reference/01-create-schema-and-tables.sql \
  sql/buildings_common/01-create-schema-and-tables.sql \
  sql/buildings/01-create-schema-and-tables.sql \
  sql/buildings_bulk_load/01-create-schema-and-tables.sql \
  sql/buildings_lds/01-create-schema-and-tables.sql \
  sql/buildings_reference/02-default-values.sql \
  sql/buildings_common/02-default-values.sql \
  sql/buildings/02-default-values.sql \
  sql/buildings_bulk_load/02-default-values.sql \
  sql/buildings_lds/02-default-values.sql \
  sql/buildings_bulk_load/03-alter_relationships_create_view.sql \
  sql/01-buildings_version.sql \
  sql/buildings_reference/functions/01-suburb_locality.sql \
  sql/buildings_reference/functions/02-town_city.sql \
  sql/buildings_reference/functions/03-territorial_authority_and_territorial_authority_grid.sql \
  sql/buildings_common/functions/01-capture_method.sql \
  sql/buildings_common/functions/02-capture_source_group.sql \
  sql/buildings_common/functions/03-capture_source.sql \
  sql/buildings/functions/01-lifecycle_stage.sql \
  sql/buildings/functions/02-use.sql \
  sql/buildings/functions/03-buildings.sql \
  sql/buildings/functions/04-building_outlines.sql \
  sql/buildings/functions/05-building_name.sql \
  sql/buildings/functions/06-building_use.sql \
  sql/buildings/functions/07-lifecycle.sql \
  sql/buildings_bulk_load/functions/01-organisation.sql \
  sql/buildings_bulk_load/functions/02-bulk_load_status.sql \
  sql/buildings_bulk_load/functions/03-qa_status.sql \
  sql/buildings_bulk_load/functions/04-supplied_datasets.sql \
  sql/buildings_bulk_load/functions/05-bulk_load_outlines.sql \
  sql/buildings_bulk_load/functions/06-existing_subset_extracts.sql \
  sql/buildings_bulk_load/functions/07-added.sql \
  sql/buildings_bulk_load/functions/08-removed.sql \
  sql/buildings_bulk_load/functions/09-related.sql \
  sql/buildings_bulk_load/functions/10-matched.sql \
  sql/buildings_bulk_load/functions/11-transferred.sql \
  sql/buildings_bulk_load/functions/12-deletion_description.sql \
  sql/buildings_bulk_load/functions/13-supplied_outlines.sql \
  sql/buildings_bulk_load/functions/14-compare_buildings.sql \
  sql/buildings_lds/functions/01-nz_building_outlines.sql \
  sql/buildings_lds/functions/02-nz_building_outlines_full_history.sql \
  sql/buildings_lds/functions/03-nz_building_outlines_lifecycle.sql \
  sql/buildings_lds/functions/04-load_buildings.sql \
  sql/buildings_lds/functions/05-populate_buildings_lds.sql \
  $(END)

# List of scripts built during install
SCRIPTS_built = \
	scripts/nz-buildings-load \
	$(END)

# List of files built from .in files during install
EXTRA_CLEAN = \
	sql/01-buildings_version.sql \
	$(SCRIPTS_built)

.dummy:

# Need install to depend on something for debuild

all: $(SQLSCRIPTS) $(SCRIPTS_built)

# Iterate through .sql.in files and build a .sql version
# with @@VERSION@@ and @@REVISION@@ replaced
%.sql: %.sql.in makefile
	$(SED) -e 's/@@VERSION@@/$(VERSION)/;s|@@REVISION@@|$(REVISION)|' $< > $@

# Replace @@VERSION@@ and @@REVISION@@ in schema load script
scripts/nz-buildings-load: scripts/nz-buildings-load.in
	$(SED) -e 's/@@VERSION@@/$(VERSION)/;s|@@REVISION@@|$(REVISION)|' $< >$@
	chmod +x $@

# Copy scripts to local data directory
# Allow nz-buildings-load to be executed from anywhere
install: $(SQLSCRIPTS) $(SCRIPTS_built)
	mkdir -p ${datadir}/sql
	cp -R sql/* ${datadir}/sql
	mkdir -p ${datadir}/tests/testdata
	cp tests/testdata/*.sql ${datadir}/tests/testdata
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
	pg_prove tests/

clean:
	# Remove the files built from .in files during install
	rm -f $(EXTRA_CLEAN)

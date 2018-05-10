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
	sql/admin_bdys/01-buildings_admin_bdys_schema.sql \
	sql/01-buildings_common_schema.sql \
	sql/02-buildings_schema.sql \
	sql/03-buildings_bulk_load_schema.sql \
	sql/04-lookup_table_values.sql \
	sql/05-buildings_version.sql \
	sql/06-compare_buildings.sql \
	sql/07-load_buildings.sql \
	sql/08-admin_boundary_functions.sql \
	sql/09-buildings_functions.sql \
	sql/10-buildings_bulk_load_functions.sql \
	sql/11-buildings_common_functions.sql \
	sql/lds/01-buildings_lds_schema.sql \
	sql/lds/02-populate_buildings_lds.sql \
	$(END)

# List of scripts built during install
SCRIPTS_built = \
	scripts/nz-buildings-load \
	$(END)

# List of files built from .in files during install
EXTRA_CLEAN = \
	sql/05-buildings_version.sql \
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
	cp sql/*.sql ${datadir}/sql
	mkdir -p ${datadir}/sql/admin_bdys
	cp sql/admin_bdys/*.sql ${datadir}/sql/admin_bdys
	mkdir -p ${datadir}/sql/lds
	cp sql/lds/*.sql ${datadir}/sql/lds
	mkdir -p ${datadir}/tests/testdata
	cp tests/testdata/*.sql ${datadir}/tests/testdata
	mkdir -p ${datadir}/tests/functiontestdata
	cp tests/functiontestdata/*.sql ${datadir}/tests/functiontestdata
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

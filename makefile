# Minimal script to install the SQL creation scripts ready for postinst script.

VERSION = dev
REVISION = $(shell test -d .git && git describe --always || echo $(VERSION))

SED = sed

datadir = ${DESTDIR}/usr/share/nz-building-outlines
bindir = ${DESTDIR}/usr/bin

SQLSCRIPTS = \
	sql/01-create_buildings_schema.sql \
	sql/02-create_buildings_stage_schema.sql \
	sql/03-insert_lookup_table_values.sql \
	sql/04-create_buildings_functions.sql \
	sql/05-buildings_version.sql \
	sql/lds/01-create_buildings_lds_schema.sql \
	$(END)

SCRIPTS_built = \
	scripts/nz-buildings-load \
	$(END)

EXTRA_CLEAN = \
    sql/05-buildings_version.sql \
    $(SCRIPTS_built)

.dummy:

# Need install to depend on something for debuild

all: $(SQLSCRIPTS) $(SCRIPTS_built)

# Iterate through .sql.in files and create a .sql version
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
	mkdir -p ${bindir}
	cp $(SCRIPTS_built) ${bindir}

uninstall:
	# Remove the SQL Scripts installed locally
	rm -rf ${datadir}

check test: $(SQLSCRIPTS)
    # Build a test database and run unit tests
	export PGDATABASE=nz-buildings-pgtap-db; \
	dropdb --if-exists $$PGDATABASE; \
	createdb $$PGDATABASE; \
	nz-buildings-load nz-buildings-pgtap-db; \
	pg_prove tests/

clean:
	# Remove the files created from .in files during install
	rm -f $(EXTRA_CLEAN)

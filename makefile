# DB

# Installs the SQL creation scripts and load script.

VERSION = dev

SED = sed

datadir = ${DESTDIR}/usr/share/nz-buildings
bindir = ${DESTDIR}/usr/bin

# List of scripts built during install
SCRIPTS_built = \
	db/scripts/nz-buildings-load \
	$(END)

# List of files built from .in files during install
EXTRA_CLEAN = \
	$(SCRIPTS_built)

.dummy:

# Need install to depend on something for debuild

all: $(SCRIPTS_built)

# Replace @@VERSION@@ and @@REVISION@@ in schema load script
db/scripts/nz-buildings-load: db/scripts/nz-buildings-load.in
	$(SED) -e 's/@@VERSION@@/$(VERSION)/' $< >$@
	chmod +x $@

# Copy scripts to local data directory
# Allow nz-buildings-load to be executed from anywhere
install: $(SCRIPTS_built)
	mkdir -p ${datadir}/sql
	cd db/sql && sqitch bundle --dest-dir ${datadir}/sql && cd -
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
	sed -i '4s/.*/dbname=nz-buildings-plugin-db/' ~/.qgis2/$(PLUGINNAME)/pg_config.ini

update_ui_headers:
	@echo
	@echo "------------------------------------------"
	@echo "Fix/revert header lines in .ui files to qgis.gui"
	@echo "------------------------------------------"
	for f in ./buildings/gui/*.ui; do \
		sed -i -e 's|<header>.*</header>|<header>qgis.gui</header>|g' $$f; \
	done; \

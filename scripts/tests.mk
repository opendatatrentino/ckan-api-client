## Makefile for running tests

## ----- Default Configuration -------------------------------
REPO_URL = https://github.com/ckan/ckan
REPO_BRANCH = master
PYTHON = /usr/bin/python2.7
CKAN_POSTGRES_ADMIN = postgresql://postgres:postgrespass@database.local/
CKAN_SOLR = http://database.local:8983/solr/ckan-2.0
CKAN_ENVS_DIR = $(shell readlink -f ./.ckan-envs)
CKAN_ENV_NAME = ckan-master
CKAN_VIRTUALENV = $(CKAN_ENVS_DIR)/$(CKAN_ENV_NAME)
PYTEST_ARGS = -vvv -rsxX --pep8 \
	--cov-report=term-missing --cov=ckan_api_client \
	$(PYTEST_EXTRA_ARGS)
PYTEST_EXTRA_ARGS = ckan_api_client/tests
##------------------------------------------------------------

all: info

info:
	@echo "--------------- Summary -------------------------"
	@echo "Python: $(shell $(PYTHON) -V 2>&1) from $(PYTHON)"
	@echo "Ckan repo url: $(REPO_URL) (branch: $(REPO_BRANCH))"
	@echo "PostgreSQL: $(CKAN_POSTRGRES_ADMIN)"
	@echo "Solr: $(CKAN_SOLR)"
	@echo "Virtualenv: $(CKAN_VIRTUALENV)"
	@echo
	@echo "Run: ``make setup`` to install virtualenv"
	@echo "Run: ``make run-tests`` to run tests"

run-tests: setup
	CKAN_VIRTUALENV=$(CKAN_VIRTUALENV) \
	CKAN_POSTGRES_ADMIN=$(CKAN_POSTGRES_ADMIN) \
	CKAN_SOLR=$(CKAN_SOLR) \
	py.test $(PYTEST_ARGS)

setup: $(CKAN_VIRTUALENV)

$(CKAN_VIRTUALENV):
	mkdir -p "$(CKAN_VIRTUALENV)"

	@# Install ckan the
	@echo "Creating virtualenv using $(shell $(PYTHON) -V 2>&1) from $(PYTHON)"
	virtualenv -p "$(PYTHON)" "$(CKAN_VIRTUALENV)"

	@# Clone repository
	@echo "Installing ckan from $(REPO_URL) (branch: $(REPO_BRANCH))"
	mkdir -p "$(CKAN_VIRTUALENV)/src"
	git clone "$(REPO_URL)" -b "$(REPO_BRANCH)" --depth=1 "$(CKAN_VIRTUALENV)/src/ckan"

	@# Install ckan
	"$(CKAN_VIRTUALENV)"/bin/pip install -r "$(CKAN_VIRTUALENV)/src/ckan/requirements.txt"
	"$(CKAN_VIRTUALENV)"/bin/pip install "$(CKAN_VIRTUALENV)/src/ckan"
	"$(CKAN_VIRTUALENV)"/bin/pip install cliff  # for some reason..

	@# Copy configuration file
	mkdir -p "$(CKAN_VIRTUALENV)/etc/ckan"
	cp "$(CKAN_VIRTUALENV)/src/ckan/ckan/config/who.ini" "$(CKAN_VIRTUALENV)/etc/ckan/who.ini"

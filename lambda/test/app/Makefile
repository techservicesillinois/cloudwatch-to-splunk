.PHONY: build test clean docker shell

LAMBDA_DIR	= app
LAMBDA_FILE	= app.py
LAMBDA_ZIP	= cloudwatch-to-splunk.zip
PACKAGE_DIR	= package
PIP_COMMAND	= pip install --no-cache-dir --quiet --upgrade
ZIP_EXCLUDES	= --exclude '*.pyc' '*/__pycache__/*'

REPO := $(shell basename $(shell git remote get-url origin) .git)

GOPTS := -lR . -e
GREP := grep $(GOPTS)
EGREP := egrep $(GOPTS)
SRCS := --include=*.tf
DOCS := --include=README.md

all: 

build:
	mkdir -p $(PACKAGE_DIR)
	$(PIP_COMMAND) --target $(PACKAGE_DIR) -r requirements.txt
	(cd $(PACKAGE_DIR); zip -qX9r ../$(LAMBDA_ZIP) . $(ZIP_EXCLUDES))
	(cd $(LAMBDA_DIR); zip -qX9 ../$(LAMBDA_ZIP) $(LAMBDA_FILE))

# Launches the Makefile inside a container
docker:
	docker build . -t test/$(REPO)
	docker run --rm test/$(REPO)

# Launches the shell inside a container for debugging the Makefile
shell:
	docker build . -t test/$(REPO)
	docker run -it --rm --entrypoint=sh test/$(REPO)

clean:
	rm -fr $(LAMBDA_ZIP) $(PACKAGE_DIR) dist *.egg-info
#	-docker rmi -f test/$(REPO) >/dev/null 2>&1

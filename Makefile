
deps/pre:
	pip install pip-tools

deps/compile:
	pip-compile

deps/install:
	pip-sync

install: deps/install

download:
	python -m src.download

transform:
ifeq ($(WARN_DUPES), true)
	python -m src.transform --warn-dupes
else
	python -m src.transform
endif

all: download transform

test:
	PYTHONPATH="src" pytest

pre-commit:
	pre-commit install
	pre-commit run --all-files

clean:
	git clean -xdf

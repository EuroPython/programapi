deps/pre:
	pip install pip-tools

deps/clean:
	rm -f requirements.txt

deps/compile:
	pip-compile

deps/install:
	pip-sync

deps/update: deps/pre deps/clean deps/compile deps/install

install: deps/install

download:
	python -m src.download

transform:
	python -m src.transform


all: download transform

test:
	PYTHONPATH="src" pytest

pre-commit:
	pre-commit install
	pre-commit run --all-files

clean:
	git clean -xdf

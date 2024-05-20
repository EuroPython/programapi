
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
	python -m src.transform


all: download transform

test:
	PYTHONPATH="src" python -m unittest;

pre-commit:
	pre-commit install
	pre-commit run --all-files

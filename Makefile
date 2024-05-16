
deps/pre:
	pip install pip-tools

deps/compile:
	pip-compile

deps/install:
	pip-sync

install: deps/install

download:
	cd src && python download.py

transform:
	cd src && python transform.py


all: download transform

test:
	PYTHONPATH="src" pytest

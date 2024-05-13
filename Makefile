
deps/pre:
	pip install pip-tools

deps/compile:
	pip-compile

deps/install:
	pip-sync

install: deps/install

update:
	mkdir -p data/
	python src/save.py

download:
	cd src && python download.py

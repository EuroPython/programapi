
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
	if pytest -v; then \
		PYTHONPATH="src" pytest; \
	else \
		echo "pytest is not found, installing pytest"; \
		pip install pytest; \
		PYTHONPATH="src" pytest; \
	fi

pre-commit:
	pre-commit install
	pre-commit run --all-files

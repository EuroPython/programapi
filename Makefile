dev:
	uv sync --dev

deps/upgrade:
	uv lock --upgrade

deps/install:
	uv sync

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
	uv run pytest

pre-commit:
	pre-commit install

clean:
	git clean -xdf

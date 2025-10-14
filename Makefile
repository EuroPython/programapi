# Optional arguments
# ==================
EXCLUDE ?=
WARN_DUPES ?= false

# Convert EXCLUDE space-separated list to repeated --exclude flags
EXCLUDE_FLAGS = $(foreach item,$(EXCLUDE),--exclude $(item))

all: download transform

download:
	python -m src.download $(EXCLUDE_FLAGS)

transform:
ifeq ($(WARN_DUPES), true)
	python -m src.transform $(EXCLUDE_FLAGS) --warn-dupes
else
	python -m src.transform $(EXCLUDE_FLAGS)
endif

test:
	uv run pytest

pre-commit:
	pre-commit install

clean:
	git clean -xdf

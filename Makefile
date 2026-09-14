# Variables for the project
# =========================
CONFERENCE ?= ep2026
DATA_DIR ?= ./data/public/$(CONFERENCE)/

# Variables for remote host
# =========================
VPS_USER  ?= static_content_user
VPS_HOST  ?= static.europython.eu
VPS_PATH  ?= /home/$(VPS_USER)/content/static/programme/$(CONFERENCE)/releases
REMOTE_CMD=ssh $(VPS_USER)@$(VPS_HOST)

# Variables for deploy
# ====================
TIMESTAMP ?= $(shell date +%Y%m%d%H%M%S)
FORCE_DEPLOY ?= false

# Optional arguments
# ==================
EXCLUDE ?=
WARN_DUPES ?= false

# Convert EXCLUDE space-separated list to repeated --exclude flags
EXCLUDE_FLAGS = $(foreach item,$(EXCLUDE),--exclude $(item))

dev:
	uv sync --dev

deps/upgrade:
	uv lock --upgrade

deps/install:
	uv sync

install: deps/install

download:
	python -m src.download $(EXCLUDE_FLAGS)

transform:
ifeq ($(WARN_DUPES), true)
	python -m src.transform $(EXCLUDE_FLAGS) --warn-dupes
else
	python -m src.transform $(EXCLUDE_FLAGS)
endif

all: download transform

ifeq ($(FORCE_DEPLOY), true)
deploy: TARGET = $(VPS_PATH)/$(TIMESTAMP)
deploy:
	@echo "\n\n**** Deploying branch '$(CONFERENCE)' to $(TARGET)...\n\n"
	$(REMOTE_CMD) "mkdir -p $(TARGET)"
	rsync -avz --delete $(DATA_DIR) $(VPS_USER)@$(VPS_HOST):$(TARGET)
	$(REMOTE_CMD) "cd $(VPS_PATH) && ln -snf $(TIMESTAMP) current"
	@echo "\n\n**** Deployment complete.\n\n"
endif

test:
	uv run pytest

pre-commit:
	pre-commit install

clean:
	git clean -xdf

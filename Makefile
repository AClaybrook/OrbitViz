# Git repository root
REPO_ROOT="$(git rev-parse --show-toplevel)"

ENV_NAME := $(REPO_ROOT)/venv2
CONDA_DIR := ~/miniconda3
PYTHON_VERSION := 3.10

.PHONY: setup requirements clean

setup:
	@echo "REPO_ROOT is: $(REPO_ROOT)"
	@echo "Creating conda environment at the repository root..."
	@conda create --prefix $(ENV_NAME) python=$(PYTHON_VERSION) -y
	@echo "Setting up hooks for the environment..."
	@ln -sf $(shell pwd)/scripts/generate_requirements.sh $(ENV_NAME)/etc/conda/activate.d/post-activate.sh
	@echo "All set! Activate your environment using: conda activate $(ENV_NAME)"

requirements:
	@bash scripts/generate_requirements.sh

clean:
	@echo "Removing environment..."
	@conda env remove --prefix $(ENV_NAME)
	@echo "Environment removed."
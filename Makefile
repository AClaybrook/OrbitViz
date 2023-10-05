# Git repository root
REPO_ROOT := $(shell git rev-parse --show-toplevel)

SHELL = /bin/bash
ENV_NAME = venv2
ENV_LOC := $(REPO_ROOT)/$(ENV_NAME)
CONDA_DIR := ~/miniconda3
PYTHON_VERSION := 3.10

.PHONY: setup requirements clean

setup:
	@echo "REPO_ROOT is: $(REPO_ROOT)"
	@echo "Creating conda environment at the repository root..."
	@conda create --prefix $(ENV_LOC) python=$(PYTHON_VERSION) -y
	@echo "Setting up hooks for the environment..."
	@mkdir -p $(ENV_LOC)/etc/conda/activate.d
	@. $(CONDA_DIR)/etc/profile.d/conda.sh && conda activate $(ENV_LOC) && conda install --file conda-requirements.txt
	@echo "All set! Your environment was activated and packages were installed. Use 'conda activate $(ENV_LOC)' to activate your environment."

requirements:
	@if [ "$$(conda info --envs | grep '*' | awk '{print $$NF}')" != "$(ENV_LOC)" ]; then \
		echo "You are not in the target environment. Please activate it with 'conda activate ./$(ENV_NAME)' and run 'make requirements' again."; \
		exit 1; \
	else \
		bash scripts/generate_requirements.sh; \
	fi

clean:
	@echo "Checking currently active environment..."
	@echo "Active environment: $$(conda info --envs | grep '*' | awk '{print $$NF}')"
	@echo "Target environment: $(ENV_LOC)"
	@if [ "$$(conda info --envs | grep '*' | awk '{print $$NF}')" = "$(ENV_LOC)" ]; then \
		echo "You are in the target environment. Please deactivate it with 'conda deactivate' and run 'make clean' again."; \
		exit 1; \
	fi
	@echo "Removing environment..."
	@conda env remove --prefix $(ENV_LOC)
	@echo "Environment removed."
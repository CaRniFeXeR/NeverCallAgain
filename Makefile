VENV_DIR ?= .venv
VENV_RUN = . $(VENV_DIR)/bin/activate


format:          ## Run black and isort code formatter
	$(VENV_RUN); python -m isort . ; python -m black .
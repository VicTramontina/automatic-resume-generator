VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: setup lint run clean

setup: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

lint: $(VENV)/bin/activate
	$(PYTHON) -m py_compile scripts/*.py

run: lint
	$(PYTHON) scripts/main.py

clean:
	rm -rf $(VENV)
	find outputs -mindepth 1 ! -name ".gitkeep" -delete

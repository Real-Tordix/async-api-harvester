PYTHON ?= python

.PHONY: test lint run gui examples

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check .

run:
	$(PYTHON) main.py

gui:
	$(PYTHON) Gui.py

examples:
	$(PYTHON) examples/basic_terminal.py

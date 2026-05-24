.PHONY: install dev test lint clean

install:
	pip install -e .

dev: install

test:
	python -m pytest tests/ -v || python -m doctest codegraph_lite/**/*.py

lint:
	python -m py_compile codegraph_lite/**/*.py
	@echo "Syntax check passed."

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .codegraph_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info 2>/dev/null || true
	@echo "Clean done."

scan:
	python -m codegraph_lite scan .

report:
	python -m codegraph_lite report .

dashboard:
	python -m codegraph_lite dashboard .

export-json:
	python -m codegraph_lite export . --format json

export-html:
	python -m codegraph_lite export . --format html

export-md:
	python -m codegraph_lite export . --format markdown

deps:
	python -m codegraph_lite deps .

complexity:
	python -m codegraph_lite complexity .

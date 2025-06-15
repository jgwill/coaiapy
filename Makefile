.PHONY: install test build sdist bdist_wheel upload clean test-release

install:
	pip install -r requirements.txt

test:
	pytest

build:
	python setup.py sdist bdist_wheel

sdist:
	python setup.py sdist

bdist_wheel:
	python setup.py bdist_wheel

upload: build
	twine upload dist/*

clean:
	rm -rf build/ dist/ *.egg-info **/*.egg-info

test-release: clean
	pip install --quiet build wheel twine
	$(MAKE) test
	python -m build
	twine upload --repository testpypi dist/*

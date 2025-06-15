.PHONY: install test build dist sdist bdist_wheel upload upload-test test-release clean

install:
	pip install -r requirements.txt

test:
	pytest

build:
	python setup.py sdist bdist_wheel

dist: build
	@echo "Distribution created in dist/"

sdist:
	python setup.py sdist

bdist_wheel:
	python setup.py bdist_wheel

upload: build
	twine upload dist/*

upload-test: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

test-release: clean build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

clean:
	rm -rf build/ dist/ *.egg-info **/*.egg-info

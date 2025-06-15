.PHONY: install test build sdist bdist_wheel upload upload-test clean

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

upload-test: build
	twine upload --repository testpypi dist/*

clean:
	rm -rf build/ dist/ *.egg-info **/*.egg-info

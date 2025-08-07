.PHONY: install test build dist sdist bdist_wheel upload upload-test test-release bump clean test-docker test-docker-clean

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
	twine upload --repository testpypi dist/*

test-release: bump clean build
	@set -a; [ -f $(HOME)/.env ] && . $(HOME)/.env; set +a; \
	twine upload --repository testpypi dist/*

bump:
	python bump.py

clean:
	rm -rf build/ dist/ *.egg-info **/*.egg-info

test-docker:
	cd tests && ./run_docker_tests.sh

test-docker-clean:
	docker rmi coaiapy-test || true

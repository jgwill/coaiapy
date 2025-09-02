.PHONY: install test build dist sdist bdist_wheel upload upload-test test-release bump clean test-docker test-docker-clean test-langfuse-real test-mobile test-mobile-quick test-mobile-performance test-mobile-compatibility test-mobile-engine test-mobile-templates test-mobile-workflows

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

test-langfuse-real:
	cd tests && ./run_real_langfuse_tests.sh

# Mobile Template Engine Test Suite
test-mobile:
	python tests/run_all_tests.py

test-mobile-quick:
	python tests/run_all_tests.py quick

test-mobile-performance:
	python tests/run_all_tests.py performance

test-mobile-compatibility:
	python tests/run_all_tests.py compatibility

test-mobile-engine:
	python tests/run_all_tests.py engine

test-mobile-templates:
	python tests/run_all_tests.py templates

test-mobile-workflows:
	python tests/run_all_tests.py workflows

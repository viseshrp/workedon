DATE = $(shell date +'%Y%m%d')

build:
	python -m build --wheel
	rm -rf build

install:
	pip uninstall workedon -y
	pip install dist/*.whl

install-dev:
	pip uninstall workedon -y
	pip install -e .
	pip install -r requirements/dev.txt

test:
	pytest -rvx --setup-show

test-cov:
	pytest -rvx --setup-show --cov=workedon \
  --cov-report html:coverage-html \
  --cov-report xml:coverage.xml \
  --cov-report term \
  --cov-config=.coveragerc

smoketest:
	workedon --help
	workedon --version

clean:
	find . -name \*.pyc -delete
	rm -rf dist \
  build \
  *.egg-info \
  .pytest_cache \
  coverage-html

clean-test:
	rm -rf .coverage \
  coverage-html \
  coverage.xml \
  .pytest_cache

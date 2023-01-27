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
	pytest -rvx --setup-show --cov=workedon --cov-report xml:coverage.xml --cov-report term

smoketest:
	workedon --help
	workedon --version

clean:
	rm -rf dist build
	rm -rf *.egg-info
	find . -name \*.pyc -delete
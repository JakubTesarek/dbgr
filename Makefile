all:
	@echo 'make clean | build | publish | test | documentation'

clean:
	rm -rf *.pyc __pycache__
	rm -rf kwargs.egg-info build dist
	cd docs && $(MAKE) clean

build: clean
	python setup.py sdist bdist_wheel

publish:
	twine check dist/*
	twine upload dist/*

lint:
	pylint app.py dbgr

test:
	py.test tests/* \
		--cov dbgr \
		--cov-config .coveragerc \
		--cov-report html \
		--cov-report term \
		--cov-fail-under=100

documentation:
	cd docs && $(MAKE) html

spelling:
	cd docs && $(MAKE) spelling

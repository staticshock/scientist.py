SHELL := bash

.PHONY: sdist
sdist:
	@python setup.py sdist

.PHONY: bdist_wheel
bdist_wheel:
	@python setup.py bdist_wheel

.PHONY: publish
publish: sdist bdist_wheel
	@[[ -f ~/.pypirc ]] || python setup.py register
	@twine upload dist/*

.PHONY: clean
clean:
	@rm -rvf MANIFEST *.egg-info *.pyc {,scientist/}{*.pyc,__pycache__}
	@rm -rvf build dist

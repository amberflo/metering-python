test:
	coverage run --branch --include 'metering/*' --omit '*test*' -m unittest metering/test/*.py

release:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

e2e_test:
	.buildscripts/e2e.sh

.PHONY: test release e2e_test

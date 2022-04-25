.PHONY: test
test:
	coverage run --branch --include 'metering/*' --omit '*test*' -m unittest metering/test/*.py

.PHONY: release
release:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

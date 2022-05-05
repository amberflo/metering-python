.PHONY: coverage
coverage:
	coverage run --branch --include 'metering/*' --omit 'tests/*' -m unittest discover
	coverage report --show-missing

.PHONY: release
release:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

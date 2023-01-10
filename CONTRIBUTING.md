# Contributors Guide

- We support Python 3.5 to 3.10.

## Setting up the dev environment

Just create a virtual environment and install the requirements.
```
python3 -m virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Testing

Run all tests:
```
python3 -m unittest discover
```

To run a specific test:
```
python3 -m unittest tests.integration.test_session.TestApiSession.test_good_response_is_parsed
```

For the integration tests, you'll need some environment variables ([details](tests/integration/README.md)).

## Code standards

- We lint the whole code using [Flake8](https://flake8.pycqa.org/en/latest/).

- We format the whole code using [Black](https://black.readthedocs.io/en/stable/).

- We keep test coverage level high.

- We prefer integration tests for the API clients and session classes.

- We keep one class per file.

## Architecture overview

The Python SDK exposes different "Api Client" classes, depending on the main
resource in question (e.g. customer, usage, product plan, etc...).

These classes are simple wrappers around the `requests.Session` class.

API call errors are detected and turned into exceptions (`ApiError`).

### High Throughput Ingestion

In order to allow high ingestion throughput without imposing significant
latency on the caller, the SDK provides an ingestion client based on the
producer-consumer pattern with an in-memory queue.

`ingest.ThreadedProducer` can be instantiated as a global variable and its
`send` method can be called by multiple threads.

The producer instance will manage a a configurable amount of background threads
(`ingest.ThreadedConsumer`). These will consume the items from the queue in
batches and send them to Amberflo.

## Making a new release

We follow [semantic versioning](https://semver.org/).

Releasing a new version is mostly automated by a Github action. It does require a few manual steps:

1. Update `VERSION` in `metering/version.py` to the new version.
2. Add an entry to `HISTORY.md` describing what's new.
3. Commit the changes
```
git commit -m "Release X.Y.Z."
```
4. Create a new tag
```
git tag "vX.Y.Z"
```
5. Push and then create a release in [Github](https://github.com/amberflo/metering-python/releases). Once you publish it, the Github action will publish the package to PyPI.

# Integration Tests

The tests here will make real requests to the external APIs (Amberflo's or otherwise).

They'll expect credentials to be available as environment variables:

- `TEST_API_KEY` for Amberflo's API.

- `TEST_BUCKET_NAME`, `TEST_ACCESS_KEY`, `TEST_SECRET_KEY` for the S3 ingestion bucket.

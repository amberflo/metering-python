import unittest

from metering.ingest import create_ingest_client
from metering.ingest import IngestApiClient, IngestS3Client


class TestCreateIngestClient(unittest.TestCase):
    def test_create_api_client(self):
        client = create_ingest_client(api_key="foo")
        self.assertIsInstance(client.consumers[0].backend, IngestApiClient)

    def test_create_s3_client(self):
        client = create_ingest_client(bucket_name="foo")
        self.assertIsInstance(client.consumers[0].backend, IngestS3Client)

    def test_create_s3_client_with_keys(self):
        client = create_ingest_client(
            bucket_name="foo", access_key="access_key", secret_key="secret_key"
        )
        self.assertIsInstance(client.consumers[0].backend, IngestS3Client)

    def test_create_api_client_with_all_options(self):
        def _on_error(*args, **kwargs):
            pass

        client = create_ingest_client(
            api_key="foo",
            max_queue_size=200000,
            threads=3,
            retries=4,
            batch_size=1000,
            send_interval_in_secs=0.7,
            sleep_interval_in_secs=0.5,
            on_error=_on_error,
        )
        self.assertIsInstance(client.consumers[0].backend, IngestApiClient)
